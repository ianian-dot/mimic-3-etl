# MIMIC-III ETL & Modelling Project

This repository contains my exploratory ETL and modelling work using the **MIMIC-III critical care dataset**.  
The goal is to clean and merge key clinical tables, engineer useful features, and build a baseline predictive model for **ICU mortality**.

## 📦 ETL & Feature Engineering

This project processes the following MIMIC-III tables:

- `PATIENTS`  
- `ADMISSIONS`  
- `DIAGNOSES_ICD`  
- `ICUSTAYS`  
- `LABEVENTS`

Main ETL steps include:

- Cleaning and validating datetime columns  
- Consolidating date-of-death fields and handling de-identified ages  
- Engineering features such as age, ethnicity groups, time-to-ICU, and ICU visit order  
- Grouping ICD-9 diagnoses and computing Charlson Comorbidity Index  
- Extracting and aggregating key laboratory measurements (mean, min, max, count) for each ICU stay  
- Merging all cleaned tables into an ICU-level analysis dataset  

## 🤖 ICU Mortality Modelling

A simple baseline model was developed to predict **ICU mortality**, using:

- Demographics  
- Comorbidity burden  
- Admission and ICU metadata  
- Laboratory features  

Models tested:

- **Logistic Regression**  
- **Random Forest**  
- **XGBoost**

Because the outcome is imbalanced (≈ 7.5% mortality), class weighting was applied.  
Evaluation included ROC–AUC, precision/recall, and basic model comparison.

## ⚠️ Notes

- **No raw MIMIC data is included** in this repository.  
- Parquet, CSV, and other data files are excluded via `.gitignore`.  
- Notebook outputs are cleared before committing.  
- This project is for personal learning in ETL, clinical data processing, and modelling.
