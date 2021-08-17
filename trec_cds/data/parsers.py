import logging
import os
import re
import xml.etree.ElementTree as ET
from glob import glob
from typing import List, Union, Tuple

import tqdm

from trec_cds.data.clinical_trial import ClinicalTrial
from trec_cds.data.topic import Topic
from trec_cds.data.utils import Gender


def load_topics_from_xml(topic_file: str) -> List[Topic]:
    """Parses topics from single XML file and creates a Topic class instance for
    each parsed item.

    :param topic_file: str
    :return: List of topics
    """
    tree = ET.parse(topic_file)
    root = tree.getroot()

    topics = []
    for elem in root:
        topics.append(Topic(number=elem.attrib["number"], text=elem.text))

    return topics


def safe_get_item(item_name: str, root: ET) -> str:
    item = root.find(item_name)
    if item:
        return item.text
    else:
        return ""


def parse_criteria(criteria: str) -> Union[None, Tuple[List[str], List[str]]]:
    """Tries to parse the criteria xml element to find and extract inclusion and
    exclusion criteria for a study.
    It uses heuristics defined based on the dataset:
    - incl/excl criteria start with a header and are sorted inclusion first,
    - every criterion starts from a newline with a number or a '-' character.

    :param criteria:
    :return: if couldn't find any criteria returns None
    """
    inclusion_criteria_strings = [
        "Inclusion Criteria",
        "Inclusion criteria",
        "Inclusive criteria",
        "INCLUSION CRITERIA",
    ]
    for inclusion_criteria_string in inclusion_criteria_strings:
        if criteria.find(inclusion_criteria_string) != -1:
            criteria_after_split = criteria.split(inclusion_criteria_string)
            break
        else:
            criteria_after_split = criteria

    if len(criteria_after_split) == 2:
        empty, tmp_inclusion = criteria_after_split
    elif len(criteria_after_split) == 1:
        return None
    else:
        return None

    if empty.strip().lower() not in ["", "key", "-", "main"]:
        logging.debug(
            "parse_criteria: skipping not parsed text after split: %s", empty.strip()
        )

    exclusion_criteria_strings = [
        "Exclusion Criteria",
        "Exclusion criteria",
        "Exclusive criteria",
        "EXCLUSION CRITERIA",
        "ECLUSION CRITERIA",
        "EXCLUSION CRITIERIA",
    ]
    for exclusion_criteria_string in exclusion_criteria_strings:
        if tmp_inclusion.find(exclusion_criteria_string) != -1:
            inclusion_exclusion_split = tmp_inclusion.split(exclusion_criteria_string)
            break
        else:
            inclusion_exclusion_split = [tmp_inclusion]

    exclusion = ""
    if len(inclusion_exclusion_split) == 2:
        inclusion, exclusion = inclusion_exclusion_split
    elif len(inclusion_exclusion_split) == 1:
        inclusion = inclusion_exclusion_split[0]
    else:
        return None

    inclusions = []
    if inclusion.strip():
        for criterion in re.split(r" - | \d\. ", inclusion):
            if criterion.strip() and criterion.strip() != ":":
                criterion = re.sub(r"[\r\n\t ]+", " ", criterion)
                inclusions.append(criterion)
    else:
        return None

    exclusions = []
    if exclusion.strip():
        for criterion in re.split(r" - | \d\. ", exclusion):
            if criterion.strip() and criterion.strip() != ":":
                criterion = re.sub(r"[\r\n\t ]+", " ", criterion)
                exclusions.append(criterion)

    return inclusions, exclusions


def parse_age(age_string: str) -> Union[int, float, None]:
    if age_string:
        if age_string in ["N/A", "None"]:
            return None

        match = re.search(r"(\d{1,2}) Year[s]?", age_string)
        if match is not None:
            return int(match.group(1))

        match = re.search(r"(\d{1,2}) Month[s]?", age_string)
        if match is not None:
            return int(match.group(1)) / 12

        match = re.search(r"(\d{1,2}) Week[s]?", age_string)
        if match is not None:
            return int(match.group(1)) / 52

        match = re.search(r"(\d{1,2}) Day[s]?", age_string)
        if match is not None:
            return int(match.group(1)) / 365

        match = re.search(r"(\d{1,2}) Hour[s]?", age_string)
        if match is not None:
            return int(match.group(1)) / 8766

        match = re.search(r"(\d{1,2}) Minute[s]?", age_string)
        if match is not None:
            return int(match.group(1)) / 525960

        logging.warning("couldn't parse ag from %s", age_string)
        return None

    return None


def parse_gender(gender_string: Union[str, None]) -> Gender:
    if gender_string == "All":
        return Gender.all
    elif gender_string == "Male":
        return Gender.male
    elif gender_string == "Female":
        return Gender.female
    else:
        return Gender.unknown  # most probably gender criteria were empty


def parse_health_status(healthy_volunteers: Union[str, None]) -> bool:
    if healthy_volunteers == "Accepts Healthy Volunteers":
        return True
    elif healthy_volunteers == "No":
        return False
    else:
        # if there is no data to exclude a patient we assume
        # that it is possible to include healthy
        return True


def parse_clinical_trials_from_folder(
        folder_name: str, first_n: Union[None, int] = None
) -> List[ClinicalTrial]:
    files = [y for x in os.walk(folder_name) for y in glob(os.path.join(x[0], "*.xml"))]

    if first_n:
        files = files[:first_n]

    total_parsed = 0

    clinical_trials = []
    for file in tqdm.tqdm(files):
        tree = ET.parse(file)
        root = tree.getroot()

        org_study_id = getattr(root.find("id_info").find("org_study_id"), "text", None)
        nct_id = getattr(root.find("id_info").find("nct_id"), "text", None)

        brief_summary = root.find("brief_summary")
        if brief_summary:
            brief_summary = brief_summary[0].text

        if not brief_summary:
            brief_summary = ""

        description = root.find("detailed_description")
        if description:
            description = description[0].text

        if not description:
            description = ""

        brief_title = safe_get_item(item_name="brief_title", root=root)
        official_title = safe_get_item(item_name="official_title", root=root)

        inclusion = []
        exclusion = []
        eligibility = root.find("eligibility")
        if not eligibility:
            criteria = ""
            gender = ""
            minimum_age = ""
            maximum_age = ""
            healthy_volunteers = ""
        else:
            criteria = eligibility.find("criteria")
            if criteria:
                criteria = criteria[0].text
                result = parse_criteria(criteria=criteria)
                if result:
                    total_parsed += 1
                    inclusion = result[0]
                    exclusion = result[1]
            else:
                criteria = ""

            gender = getattr(eligibility.find("gender"), "text", None)
            minimum_age = getattr(eligibility.find("minimum_age"), "text", None)
            maximum_age = getattr(eligibility.find("maximum_age"), "text", None)
            healthy_volunteers = getattr(
                eligibility.find("healthy_volunteers"), "text", None
            )

        gender = parse_gender(gender)
        minimum_age = parse_age(minimum_age)
        maximum_age = parse_age(maximum_age)
        healthy_volunteers = parse_health_status(healthy_volunteers)

        text: str = brief_title + official_title + brief_summary + criteria
        if text.strip() == "":
            text = "empty"

        clinical_trials.append(
            ClinicalTrial(
                org_study_id=org_study_id,
                nct_id=nct_id,
                summary=brief_summary,
                description=description,
                criteria=criteria,
                gender=gender,
                minimum_age=minimum_age,
                maximum_age=maximum_age,
                healthy_volunteers=healthy_volunteers,
                inclusion=inclusion,
                exclusion=exclusion,
                brief_title=brief_title,
                official_title=official_title,
                text=text,
            )
        )

    if len(files) > 0:
        print(
            f"percentage of successfully parsed criteria : {total_parsed / len(files)}"
        )

    return clinical_trials
