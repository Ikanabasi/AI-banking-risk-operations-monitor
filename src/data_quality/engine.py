import pandas as pd # type: ignore
from src.data_quality.validators import (
    validate_required,
    validate_numeric,
    validate_datetime,
    validate_range,
    validate_allowed_values,
    validate_pattern,
    validate_unique
)
import re # type: ignore

def split_valid_rejected(dataframe, valid_mask, rejection_reason):
    clean_dataframe = dataframe[valid_mask].copy()
    rejected_dataframe = dataframe[~valid_mask].copy()
    rejected_dataframe['rejection_reason'] = rejection_reason
    return clean_dataframe, rejected_dataframe  

def apply_required_rule(dataframe, column_name):

    valid_mask = (
        dataframe[column_name]
        .apply(validate_required)
    )

    rejection_reason = (
        'MISSING_' + column_name.upper()
    )

    return split_valid_rejected(
        dataframe,
        valid_mask,
        rejection_reason
    )


def apply_numeric_rule(dataframe, column_name):
    valid_mask = dataframe[column_name].apply(validate_numeric)
    #return rejected reason like 'INVALID_NUMERIC' for rejected rows
    rejection_reason = ('INVALID_' + column_name.upper())
    return split_valid_rejected(dataframe, valid_mask, rejection_reason)

def apply_datetime_rule(dataframe, column_name):

    valid_mask = dataframe[column_name].apply(validate_datetime)

    rejection_reason = (
        'INVALID_' + column_name.upper()
    )

    return split_valid_rejected(
        dataframe,
        valid_mask,
        rejection_reason
    )

def apply_range_rule(dataframe, column_name, min_value, max_value):
    valid_mask = dataframe[column_name].apply(lambda value: validate_range(value, min_value, max_value))
    rejection_reason = ('OUT_OF_RANGE_' + column_name.upper())
    return split_valid_rejected(dataframe, valid_mask, rejection_reason)

def apply_allowed_values_rule(dataframe, column_name, allowed_values):
    valid_mask = dataframe[column_name].apply(lambda value: validate_allowed_values(value, allowed_values))
    rejection_reason = ('INVALID_' + column_name.upper())
    return split_valid_rejected(dataframe, valid_mask, rejection_reason)

def apply_pattern_rule(dataframe, column_name, pattern):
    valid_mask = dataframe[column_name].apply(lambda value: validate_pattern(value, pattern))
    rejection_reason = ('INVALID_' + column_name.upper())
    return split_valid_rejected(dataframe, valid_mask, rejection_reason)

def apply_unique_rule(dataframe, column_name):
    valid_mask = validate_unique(dataframe, column_name)
    rejection_reason = ('DUPLICATE_' + column_name.upper())
    return split_valid_rejected(dataframe, valid_mask, rejection_reason)

def run_data_quality_rules(dataframe, rules):

    clean_dataframe = dataframe.copy()
    rejected_parts = []

    for rule in rules:

        rule_type = rule['type']
        column_name = rule['column_name']

        if rule_type == 'required':
            clean_dataframe, rejected = apply_required_rule(
                clean_dataframe,
                column_name
            )

        elif rule_type == 'numeric':
            clean_dataframe, rejected = apply_numeric_rule(
                clean_dataframe,
                column_name
            )

        elif rule_type == 'datetime':
            clean_dataframe, rejected = apply_datetime_rule(
                clean_dataframe,
                column_name
            )

        elif rule_type == 'range':
            clean_dataframe, rejected = apply_range_rule(
                clean_dataframe,
                column_name,
                rule.get('min_value'),
                rule.get('max_value')
            )

        elif rule_type == 'allowed_values':
            clean_dataframe, rejected = apply_allowed_values_rule(
                clean_dataframe,
                column_name,
                rule['allowed_values']
            )

        elif rule_type == 'pattern':
            clean_dataframe, rejected = apply_pattern_rule(
                clean_dataframe,
                column_name,
                rule['pattern']
            )

        elif rule_type == 'unique':
            clean_dataframe, rejected = apply_unique_rule(
                clean_dataframe,
                column_name
            )

        rejected_parts.append(rejected)

    if rejected_parts:
        rejected_dataframe = pd.concat(
            rejected_parts,
            ignore_index=True
        )
    else:
        rejected_dataframe = pd.DataFrame()

    return clean_dataframe, rejected_dataframe