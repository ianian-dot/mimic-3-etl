## CLEANING PATIENTS ----------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------
import pandas as pd 
import numpy as np
import os 


## Check 
def check_raw_data():
    if not os.path.exists(raw_dir):
        print('raw data path does not exist')
    else: 
        print(os.listdir(raw_dir))


## BASIC CLEANING AFTER READING DF
## STEP 1: BASIC CLEANING 
def standardise_col_names(df):
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    return df 

## convert to datetimes 
def convert_to_time_patients(patients):
    '''
    DETECTS COLS IN PATIENT CSV THAT CONTAIN 'DO' I.E. 'DATE OF' 
    AND THEN CONVERTS THEM TO DATETIME WITH ERRORS = 'COERCE'
    '''
    
    date_cols = [col for col in patients.columns if col.lower().startswith('do')]
    for col in date_cols:
        # print(col)
        # print('before')
        print(patients[col].dtype)
        patients[col] = pd.to_datetime(patients[col], errors = 'coerce')
        # print('after')
        print(patients[col].dtype)
        
    return patients 
    
def handle_DOD_columns(patients):

    ## Detect DOD columns
    DOD_cols = [col for col in patients.columns if col.startswith('dod')]
    if DOD_cols:
        print(DOD_cols)
    else:
        print('No DOD cols detected -- returning dataset as it is')
        return patients 

    ## prioritise DOD Hosp (i.e. if there are conflicts, then DOD hosp will be used 
    ## CREATE NEW COL: DOD_CONSOLIDATED from existing col 
    patients['DOD_consolidated'] = patients['DOD_HOSP'.lower()]

    ## next 
    patients['DOD_consolidated'] = patients['DOD_consolidated'].fillna(patients['DOD_SSN'.lower()])
    ## else 
    patients['DOD_consolidated'] = patients['DOD_consolidated'].fillna(patients['DOD'.lower()])

    ## drop the DOD columns 
    patients = patients.drop(columns = DOD_cols)
    print('Dropping DOD cols')

    return patients
    
    

#------------------------------------------------------------------------------------------------------------------------------------------
## CLEANING ADMISSIONS---------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------

def clean_ethnicity(admissions, verbose = True):
    ## Get major ethnicity categorisation 
    major_ethnic_cats = ['WHITE', 'ASIAN', 'BLACK', 'HISPANIC', 'AMERICAN INDIAN']
    
    for enthnicity in major_ethnic_cats:
        ## subset 
        print(admissions[admissions['ethnicity'].str.contains(enthnicity)].shape)
    
        ## mutate
        ## CREATES NEW COL: ETHNICITY CATEGORISED
        admissions.loc[admissions['ethnicity'].str.contains(enthnicity), 'ethnicity_categorised'] = enthnicity 

    if verbose: 
        print(admissions.ethnicity_categorised.value_counts())

    return admissions

def convert_to_time_admissions(admissions):
    time_cols = [col for col in admissions if col.lower().endswith('time')]

    ## Check if columns are already converted -- then skip
    if all(pd.api.types.is_datetime64_any_dtype(admissions[col]) for col in time_cols):
        print('columns are already datetime')
        return admissions

    for col in time_cols:
        print(f'converting {col} to dt')
        admissions[col] = pd.to_datetime(admissions[col])

    return admissions

def generate_LOS(admissions):
    # admissions['los_admission'] = admissions['DISCHTIME'] - admissions['ADMITTIME']
    admissions['los_admission'] = admissions['dischtime'] - admissions['admittime']
    return admissions
    
def remove_incorrect_ad_discharge_times(admissions, verbose = True):
    ## run this after converting to datetime 
    # incorrect_ad_times_mask = admissions['DISCHTIME'] < admissions['ADMITTIME']
    incorrect_ad_times_mask = admissions['dischtime'] < admissions['admittime']
    
    if verbose: 
        print(f'Number of incorrect" {incorrect_ad_times_mask.sum()}')

    ## drop 
    return(admissions[~incorrect_ad_times_mask])


    

def full_clean_admissions(admissions):
    df = clean_ethnicity(admissions)
    df = convert_to_time_admissions(df)
    df = generate_LOS(df)
    df = remove_incorrect_ad_discharge_times(df)

    ## clean diagnosis 
    df.loc[:, 'diagnosis'] = df.diagnosis.str.strip() 
    

    return(df)

#------------------------------------------------------------------------------------------------------------------------------------------
## CLEANING DIAGNOSIS ---------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------

## Categorise ICD 9 disease (chapter groupings)
# def icd9_chapters(diagnosis):     
#     '''
#     '''
#     ## extract first three numbers 
#     first3 = pd.to_numeric(diagnosis.icd9_code.str[:3], errors= 'coerce')
    
#     ## create masks 
#     external_causes_mask = diagnosis.icd9_code.str.startswith('E') 
#     supplementary_mask = diagnosis.icd9_code.str.startswith('V')
#     infectious_mask   = (first3 >=   0) & (first3 <= 139)
#     neoplasms_mask    = (first3 >= 140) & (first3 <= 239)
#     endocrine_mask    = (first3 >= 240) & (first3 <= 279)
#     digestive_mask    = (first3 >= 520) & (first3 <= 579)
#     genitourinary_mask    = (first3 >= 580) & (first3 <= 629)
    
#     circulatory_mask  = (first3 >= 390) & (first3 <= 459)
#     respiratory_mask  = (first3 >= 460) & (first3 <= 519)
#     trauma_mask       = (first3 >= 800) & (first3 <= 959)

    
#     ## categorise 
#     diagnosis.loc[external_causes_mask.fillna(False) ,'icd_group'] = 'External causes'
#     diagnosis.loc[supplementary_mask.fillna(False) ,'icd_group'] = 'Supplementary factors'
#     diagnosis.loc[infectious_mask.fillna(False) ,'icd_group'] = 'Infectious'
#     diagnosis.loc[neoplasms_mask.fillna(False) ,'icd_group'] = 'Neoplasms'
#     diagnosis.loc[endocrine_mask.fillna(False) ,'icd_group'] = 'Endocrine'
#     diagnosis.loc[circulatory_mask.fillna(False) ,'icd_group'] = 'Circulatory'
#     diagnosis.loc[respiratory_mask.fillna(False) ,'icd_group'] = 'Respiratory'
#     diagnosis.loc[trauma_mask.fillna(False) ,'icd_group'] = 'Trauma'

#     ## THE REST 
#     diagnosis.icd_group = diagnosis.icd_group.fillna('Others')

#     ## return 
#     return diagnosis

def icd9_chapters(diagnosis):
    first3 = pd.to_numeric(diagnosis.icd9_code.str[:3], errors='coerce')

    # Masks
    external_causes_mask = diagnosis.icd9_code.str.startswith('E')
    supplementary_mask   = diagnosis.icd9_code.str.startswith('V')

    masks = {
        'Infectious':      (first3.between(0, 139)),
        'Neoplasms':       (first3.between(140, 239)),
        'Endocrine':       (first3.between(240, 279)),
        'Blood':           (first3.between(280, 289)),
        'Mental':          (first3.between(290, 319)),
        'Nervous':         (first3.between(320, 389)),
        'Circulatory':     (first3.between(390, 459)),
        'Respiratory':     (first3.between(460, 519)),
        'Digestive':       (first3.between(520, 579)),
        'Genitourinary':   (first3.between(580, 629)),
        'Pregnancy':       (first3.between(630, 679)),
        'Skin':            (first3.between(680, 709)),
        'Musculoskeletal': (first3.between(710, 739)),
        'Congenital':      (first3.between(740, 759)),
        'Perinatal':       (first3.between(760, 779)),
        'Symptoms':        (first3.between(780, 799)),
        'Injury/Poisoning':(first3.between(800, 999)),
    }

    # Apply masks
    for label, mask in masks.items():
        diagnosis.loc[mask.fillna(False), 'icd_group'] = label

    diagnosis.loc[external_causes_mask.fillna(False), 'icd_group'] = 'External causes'
    diagnosis.loc[supplementary_mask.fillna(False), 'icd_group']   = 'Supplementary factors'

    # Fill remaining
    diagnosis['icd_group'] = diagnosis['icd_group'].fillna('Others')

    return diagnosis


#######################################################################################################################################################
## TRANSFORMANTION ####################################################################################################################################
#######################################################################################################################################################


## CLEANING PATIENTS_ADMISSIONS ----------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------

## Directly subtracting will cause an overflow error, hence need to handle carefully 

def get_age_via_extraction(df, col_end, col_start, new_age_col_name):
    '''
    Calculates the age of the patient at the point of admission 
    This is to prevent integer overflow error --> since a standard pandas datetime subtraction will produce time difference in nanoseconds (hence the values will be too large)
    e.g. 
        col_end = ADMITTIME (from admissions)
        col_start = DOB (from patients)
    '''
    ## Check that cols exist in the df:
    if (col_start not in df.columns) or (col_end not in df.columns):
        print('cols not found in df -- check spelling')
        return df
    
    ## Extract year and doy 
    year_diff = df[col_end].dt.year - df[col_start].dt.year
    dayofyear_not_reached = df[col_end].dt.dayofyear < df[col_start].dt.dayofyear
    
    ## Get age 
    df[new_age_col_name] = year_diff - dayofyear_not_reached
    
    ## done 
    return df

## Therefore need to deal with those >= 300
def pull_back_deid_ages(patients_admissions):
    deid_mask = patients_admissions.age_during_admission >= 300
    ## bring back to 90 + some noise 

    ## DEFINE THE NOISE -- RANDOM INT BETWEEN 0 AND 10 
    noise = np.random.randint(0,10, size = deid_mask.sum())

    ## ADD THE NOISE for subset 
    patients_admissions.loc[deid_mask, 'age_during_admission'] = 90 + noise 

    return patients_admissions
    

def age_categorise(patients_admissions):
    bins = [0, 18, 30, 40, 50, 60, 70, 80, 200]
    labels = ['<18','18-29','30-39','40-49','50-59','60-69','70-79','80+']

    patients_admissions['age_group'] = pd.cut(patients_admissions['age_during_admission'], bins=bins, labels=labels, right=False)
    return patients_admissions

    
