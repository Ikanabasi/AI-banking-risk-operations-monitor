import pandas as pd

def create_copy(df):
    return df.copy()

def amount_to_numeric(amount):
    return pd.to_numeric(amount, errors='coerce')

def column_to_datetime(column):
    return pd.to_datetime(column, errors='coerce').dt.normalize()

def standardize_string(string):
    return string.str.upper().str.strip()

def clean_merchant(merchant):
    return merchant.str.capitalize().str.strip()




