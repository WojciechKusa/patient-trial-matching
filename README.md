TREC-cds
==============================

TU Wien @ TREC 2021 Clinical Trials Task


## Installation

Install requirements with:

```bash
$ pip install -r requirements.txt 
```

This will install all required packages and also this project in a devel mode.


## Data

Data from TREC-CDS is stored in `data/external` directory. It contains:

* `topics2021.xml` file with 75 patients' data
* 5 .zip files with ClinicalTrials data

ClinicalTrials are stored with [git LFS](https://git-lfs.github.com) and after downloading should be extracted into `data/external/ClinicalTrials/` folder.


## Usage

After successful installation and configuration of the datasets just run:

```bash
$ python trec_cds/main.py
```

## Text annotations for named entities

Annotation schema 0.1.0

- Age (Numerical)
- Gender (M / F / O)
- Disease
- Chemical  (Drugs, etc.)
- Dosage (relation with Chemical, also duration?)
- Examination (CT / MR / etc.)
- Examination results (relation with EXA)
- Procedure (Surgery)
- Symptom 
- Ethnicity 

others for consideration:

- Healthiness ? ("healthy")
- Date


### Acronyms used in text

- h/o - history of
- S/P - Told Stimulant/Got Placebo
- w/ - with
- w/o - without
- Pt - patient
- Tx - treatment, therapy, ?transfer?
- XRT - radiotherapy
- CXR - chest X-ray
- SOB - shortness of breath


Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
