import pandas as pd # type: ignore
import re

def validate_required(value):
    if pd.isna(value) or str(value).strip() == '':
        return False
    return True

def validate_numeric(value):
    if pd.isna(value):
        return False
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
    
def validate_datetime(value):
    if pd.isna(value):
        return False
    
    converted_value = pd.to_datetime(value, errors='coerce')

    if pd.isna(converted_value):
        return False
    return True

def validate_range(value, min_value=None, max_value=None):
    if pd.isna(value):
        return False
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True

def validate_allowed_values(value, allowed_values):
    if pd.isna(value):
        return False
    if allowed_values is not None and value not in allowed_values:
        return False
    return True

def validate_pattern(value, pattern):
    if pd.isna(value):
        return False
    if not re.match(pattern, str(value)):
        return False
    return True

def validate_unique(dataframe, column_name):
    valid_mask = ~dataframe[column_name].duplicated(keep=False)
    return valid_mask