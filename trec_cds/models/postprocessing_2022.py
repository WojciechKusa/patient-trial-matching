import json
import logging
from typing import Dict, List

import pandas as pd

from trec_cds.data.load_data_from_file import load_jsonl
from trec_cds.features.build_features import ClinicalTrialsFeatures
import datetime
from trec_cds.models.trec_evaluation import load_qrels, print_line, read_bm25
import pytrec_eval
from typing import List
from tqdm import tqdm
import logging
import pandas as pd
import json
import os

from CTnlp.utils import Gender


def add_filter_for_x(ct, x: List[str]):
    accepts_x = None
    inclusion_occurence = 0
    exclusion_occurence = 0
    for keyword in x:
        if keyword in ct['inclusion_criteria']['positive_entities']:
            inclusion_occurence += 1
        if keyword in ct['inclusion_criteria']['negated_entities']:
            inclusion_occurence -= 1
    for keyword in x:
        if keyword in ct['exclusion_criteria']['positive_entities']:
            exclusion_occurence -= 1
        if keyword in ct['exclusion_criteria']['negated_entities']:
            exclusion_occurence += 1

    if inclusion_occurence + exclusion_occurence > 0:
        accepts_x = True
    elif inclusion_occurence + exclusion_occurence < 0:
        accepts_x = False
    else:
        accepts_x = 'No info'
    return accepts_x


def create_new_filters(cts):
    for ct in cts:
        ct['accepts_smokers'] = add_filter_for_x(ct, x=['smoking', 'smoke'])
        ct['accepts_drinkers'] = add_filter_for_x(ct, x=['alcohol'])
    return cts

def postprocessing(
    result_filename: str,
    output_file: str,
    clinical_trials_dict: Dict[str, Dict[str, str]],
    patients: List[Dict[str, str]],
):
    """Post processes result file by removing gender, age and health status mismatches
    between topic and clinical trial data."""
    with open(result_filename) as fp:
        results = json.load(fp)

    total_checked = 0
    total_excluded = 0

    output_scores = {}
    for topic_no in results:
        included = {}
        logging.info(topic_no)
        excluded_num = 0
        checked = 0

        for nct_id, score in results[topic_no].items():
            gender = patients[int(topic_no) - 1]['gender']
            age = patients[int(topic_no) - 1]['age']
            is_smoker = patients[int(topic_no) - 1]['is_smoker']
            is_drinker = patients[int(topic_no) - 1]['is_drinker']

            clinical_trial = clinical_trials_dict.get(nct_id, {})
            if clinical_trial:
                checked += 1
                if clinical_trial['gender'] != gender and clinical_trial['gender'] not in [
                    "A",
                    "U",
                ]:
                    logging.info("gender mismatch")
                    excluded_num += 1
                    continue

                if (
                    age != -1
                    and clinical_trial['minimum_age']
                    and age < clinical_trial['minimum_age']
                ):
                    logging.info("skipping because of minimum_age age")
                    excluded_num += 1
                    continue
                if (
                    age != -1
                    and clinical_trial['maximum_age']
                    and age > clinical_trial['maximum_age']
                ):
                    logging.info("skipping because of maximum_age age")
                    excluded_num += 1
                    continue

                if is_smoker and not clinical_trial['accepts_smokers']:
                    logging.info("skipping because of smoker and trial does not accept smokers")
                    excluded_num += 1
                    continue

                if (is_drinker and not clinical_trial['accepts_drinkers']):
                    logging.info("skipping because of drinker and trial does not accept drinkers")
                    excluded_num += 1
                    continue

            included[nct_id] = score

        output_scores[topic_no] = included
        total_checked += checked
        total_excluded += excluded_num
        print(f"{topic_no=} - {len(included)=} - {checked=}, excluded {excluded_num=}")

    print(
        f"{total_checked=} - {total_excluded=} - \
        percentage of excluded {total_excluded / total_checked}%"
    )

    with open(output_file, "w") as fp:
        json.dump(output_scores, fp)


if __name__ == "__main__":
    # lemma = 'lemma'
    lemma = 'not_lemma'

    submission_folder = '/newstorage4/wkusa/data/trec_cds/data/submissions/'


    trials_file = "/newstorage4/wkusa/data/trec_cds/trials_parsed-new.jsonl"
    trials = load_jsonl(trials_file)
    trials = create_new_filters(trials)

    cts_dict = {ct['nct_id']: ct for ct in trials}

    # "bm25p-submission_topics2021_not_lemma_pnfp_eligibility_all-text_cmh-keywords-2022-08-28"
    output_file = ""
    for patient_file in ['topics2022']:
        # first_stage_results_file = f"{submission_folder}/bm25p-submission_{patient_file}_{lemma}-2022-08-28 12:05:34.101636.json"
        first_stage_results_file = f"{submission_folder}/bm25p-submission_{patient_file}_{lemma}_pnf_eligibility_all-text_cmh-keywords-2022-08-28.json"
        run_name = f"submission_{patient_file}_{lemma}"

        infile = f"/home/wkusa/projects/TREC/trec-cds1/data/processed/{patient_file}.jsonl"
        patients = load_jsonl(infile)

        postprocessing(
            result_filename=first_stage_results_file,
            output_file=f"{submission_folder}/bm25p-postprocessed-{patient_file}-{lemma}_pnf_eligibility_all-text_all-keywords.json",
            clinical_trials_dict=cts_dict,
            patients=patients,
        )
