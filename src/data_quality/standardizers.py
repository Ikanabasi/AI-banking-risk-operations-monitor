import pandas as pd # type: ignore

def standardize_string(value):
    if pd.isna(value):
        return value
    return str(value).strip().upper()

def standardize_identifier(value):
    if pd.isna(value):
        return value
    return str(value).strip().upper()

def standardize_string_column(dataframe, column_name):

    dataframe = dataframe.copy()
    dataframe[column_name] = dataframe[column_name].apply(standardize_string)

    return dataframe

def convert_numeric_column(dataframe, column_name):

    dataframe = dataframe.copy()
    dataframe[column_name] = pd.to_numeric(dataframe[column_name], errors='coerce')

    return dataframe

def convert_datetime_column(dataframe, column_name):

    dataframe = dataframe.copy()
    dataframe[column_name] = pd.to_datetime(dataframe[column_name], errors='coerce')

    return dataframe