# MIMIC-III ETL Project

This repository contains my exploratory ETL work using the MIMIC-III dataset.  
The goal is to clean, transform, and merge core clinical tables including:

- PATIENTS  
- ADMISSIONS  
- DIAGNOSES_ICD  
- ICUSTAYS  

I build features such as age, diagnosis groups, ICU visit sequencing, time-to-ICU, and ICU mortality indicators.  
The final cleaned and transformed tables are saved locally as Parquet files for downstream analysis or modelling.

## What this project includes
- Cleaning of datetime columns and validation of timestamps  
- Consolidating multiple date-of-death fields  
- Computing age at admission and age at death  
- ICD-9 chapter grouping for diagnoses  
- Joining patients, admissions, and diagnoses  
- Cleaning ICU stays and engineering ICU-level features  
- Exploratory summaries (admission frequency, mortality rates, diagnoses by ethnicity/age)

## Notes
- **No raw MIMIC data is included in this repository.**  
- All notebook outputs should be cleared before committing.  
- Parquet and CSV files are excluded for compliance and privacy.

This project is for personal learning and practice in ETL, clinical data pipelines, and data engineering.
