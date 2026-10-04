import pandas as pd # type: ignore

def standardize_string(value):
    if pd.isna(value):
        return value
    return str(value).strip().upper()

def validate_required(value):
    if pd.isna(value) or str(value).strip() == '':
        return False
    return True

def clean_required_string_column(dataframe, column_name):

    dataframe = dataframe.copy()
    dataframe[column_name] = dataframe[column_name].apply(standardize_string)

    #check which values pass the required-field rule
    valid_mask = dataframe[column_name].apply(validate_required)

    rejected_dataframe = dataframe[~valid_mask].copy()
    rejected_dataframe['rejection_reason'] = 'REQUIRED_' + column_name.upper()

    #only valid rows continue through the pipeline
    clean_dataframe = dataframe[valid_mask].copy()

    return clean_dataframe, rejected_dataframe


