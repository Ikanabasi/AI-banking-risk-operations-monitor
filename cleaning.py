import pandas as pd # type: ignore

def load_data(filepath):
    return pd.read_csv(filepath)

def clean_customer_id(transactions, accounts):

    # Get only the columns we need from the accounts table
    account_lookup = accounts[['account_id', 'customer_id']].copy()

    # Rename customer_id so it does not clash with the one
    # already inside the transactions dataframe
    account_lookup = account_lookup.rename(
        columns={'customer_id': 'customer_id_from_accounts'}
    )

    # Join the transactions with the account reference data
    merged = transactions.merge(
        account_lookup,
        on='account_id',
        how='left'
    )

    # Only fill customer_id where it is currently missing
    merged['customer_id'] = merged['customer_id'].fillna(
        merged['customer_id_from_accounts']
    )

    # We no longer need the temporary lookup column
    merged = merged.drop(columns=['customer_id_from_accounts'])

    return merged

def clean_account_id(transactions, accounts):

    # 1. Count how many unique accounts each customer has
    account_counts = (
        accounts.groupby('customer_id')['account_id']
        .nunique()
    )

    # 2. Find customers that have exactly ONE account
    single_account_customers = (
        account_counts[account_counts == 1].index
    )

    # 3. Build a lookup table for ONLY those customers
    account_lookup = accounts[
        accounts['customer_id'].isin(single_account_customers)
    ][['customer_id', 'account_id']].copy()


    # Rename account_id so it does not clash with the
    # existing account_id in transactions
    account_lookup = account_lookup.rename(
        columns={
            'account_id': 'account_id_from_accounts'
        }
    )

    # 4. Merge the safe lookup into the transactions
    merged = transactions.merge(
        account_lookup,
        on='customer_id',
        how='left'
    )

    # 5. Fill missing account_id ONLY when there is one
    #    possible account for that customer
    merged['account_id'] = merged['account_id'].fillna(
        merged['account_id_from_accounts']
    )


    # Remove temporary lookup column
    merged = merged.drop(
        columns=['account_id_from_accounts']
    )

    # 6. Find transactions that STILL have no account_id
    unresolved_accounts = merged[
        merged['account_id'].isna()
    ].copy()

    # 7. Find how many possible accounts each unresolved
    #    customer has
    unresolved_accounts['possible_account_count'] = (
        unresolved_accounts['customer_id']
        .map(account_counts)
        .fillna(0)
        .astype(int)
    )

    # 8. More than one possible account = ambiguous
    ambiguous_accounts = unresolved_accounts[
        unresolved_accounts['possible_account_count'] > 1
    ].copy()

    ambiguous_accounts['rejection_reason'] = (
        'AMBIGUOUS_ACCOUNT'
    )

    # 9. Zero matching accounts = missing account
    missing_accounts = unresolved_accounts[
        unresolved_accounts['possible_account_count'] == 0
    ].copy()

    missing_accounts['rejection_reason'] = (
        'MISSING_ACCOUNT'
    )

    # 10. Put both rejected groups together
    rejected_accounts = pd.concat(
        [
            ambiguous_accounts,
            missing_accounts
        ],
        ignore_index=True
    )

    # 11. Return:
    #     - transactions after safe account recovery
    #     - rows that need quarantine
    return merged, rejected_accounts


def clean_datetime(transactions, datetime_columns):

    rejected_list = []

    for column in datetime_columns:

        transactions[column] = pd.to_datetime(
            transactions[column],
            errors='coerce'
        )

        rejected = transactions[
            transactions[column].isna()
        ].copy()

        rejected['rejection_reason'] = (
            'INVALID_' + column.upper()
        )

        rejected_list.append(rejected)

    rejected_datetime = pd.concat(
        rejected_list,
        ignore_index=True
    )

    return transactions, rejected_datetime

def currency_code(transactions, currency_column):

    transactions[currency_column] = transactions[currency_column].astype(str).str.upper()

    # Find rows where currency code is invalid (not 3 letters)
    rejected_currency = transactions[
        ~transactions[currency_column].str.match(r'^[A-Z]{3}$')
    ].copy()

    # Record exactly why they failed
    rejected_currency['rejection_reason'] = (
        'INVALID_' + currency_column.upper()
    )

    return transactions, rejected_currency

def merchant_id(transactions, merchant_column):

    transactions[merchant_column] = transactions[merchant_column].astype(str)

    # Find rows where merchant ID is invalid (empty string)
    rejected_merchant = transactions[
        transactions[merchant_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_merchant['rejection_reason'] = (
        'INVALID_' + merchant_column.upper()
    )

    return transactions, rejected_merchant


def clean_merchant_name(transactions, merchants):

    # Keep only the columns needed from the merchants reference table
    merchant_lookup = merchants[
        ['merchant_id', 'merchant_name']
    ].copy()

    # Rename merchant_name from the reference table
    # so it does not clash with the transaction column
    merchant_lookup = merchant_lookup.rename(
        columns={
            'merchant_name': 'merchant_name_from_reference'
        }
    )

    # Merge transactions with the merchant reference table
    transactions = transactions.merge(
        merchant_lookup,
        on='merchant_id',
        how='left'
    )

    # Fill missing merchant names using the reference table
    transactions['merchant_name'] = transactions[
        'merchant_name'
    ].fillna(
        transactions['merchant_name_from_reference']
    )

    # Remove the temporary helper column
    transactions = transactions.drop(
        columns=['merchant_name_from_reference']
    )

    # Find rows that still have no merchant name
    rejected_merchant_name = transactions[
        transactions['merchant_name'].isna()
    ].copy()

    # Add rejection reason
    rejected_merchant_name['rejection_reason'] = (
        'MISSING_MERCHANT_NAME'
    )

    return transactions, rejected_merchant_name

def clean_merchant_category(transactions, merchant_category_column):

    transactions[merchant_category_column] = transactions[merchant_category_column].astype(str).str.upper()

    # Find rows where merchant category is invalid (empty string)
    rejected_merchant_category = transactions[
        transactions[merchant_category_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_merchant_category['rejection_reason'] = (
        'INVALID_' + merchant_category_column.upper()
    )

    return transactions, rejected_merchant_category

def clean_transaction_type(transactions, transaction_type_column):

    transactions[transaction_type_column] = transactions[transaction_type_column].astype(str).str.upper()

    # Find rows where transaction type is invalid (empty string)
    rejected_transaction_type = transactions[
        transactions[transaction_type_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_transaction_type['rejection_reason'] = (
        'INVALID_' + transaction_type_column.upper()
    )

    return transactions, rejected_transaction_type

def clean_payment(transactions, payment_method_column):

    transactions[payment_method_column] = transactions[payment_method_column].astype(str).str.upper()

    # Find rows where payment method is invalid (empty string)
    rejected_payment_method = transactions[
        transactions[payment_method_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_payment_method['rejection_reason'] = (
        'INVALID_' + payment_method_column.upper()
    )

    return transactions, rejected_payment_method

def clean_channel(transactions, channel_column):

    transactions[channel_column] = transactions[channel_column].astype(str).str.upper()

    # Find rows where channel is invalid (empty string)
    rejected_channel = transactions[
        transactions[channel_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_channel['rejection_reason'] = (
        'INVALID_' + channel_column.upper()
    )

    return transactions, rejected_channel

def clean_city(transactions, city_column):

    transactions[city_column] = transactions[city_column].astype(str).str.upper()

    # Find rows where city is invalid (empty string)
    rejected_city = transactions[
        transactions[city_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_city['rejection_reason'] = (
        'INVALID_' + city_column.upper()
    )

    return transactions, rejected_city

def province_state(transactions, province_state_column):

    transactions[province_state_column] = transactions[province_state_column].astype(str).str.upper()

    return transactions

def clean_country(transactions, country_column):

    transactions[country_column] = transactions[country_column].astype(str).str.upper()

    # Find rows where country is invalid (empty string)
    rejected_country = transactions[
        transactions[country_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_country['rejection_reason'] = (
        'INVALID_' + country_column.upper()
    )

    return transactions, rejected_country

def description(transactions, description_column):

    transactions[description_column] = transactions[description_column].astype(str).str.upper()

    #if description is empty, do transaction type + '-' + merchant name and fillna
    transactions[description_column] = transactions[description_column].fillna(
        transactions['transaction_type'].astype(str).str.upper() + '-' + transactions['merchant_name'].astype(str).str.upper()
    )

    rejected_description = transactions[
        transactions[description_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_description['rejection_reason'] = (
        'INVALID_' + description_column.upper()
    )

    return transactions, rejected_description

def clean_source_system(transactions, source_system_column):

    transactions[source_system_column] = transactions[source_system_column].astype(str).str.upper()

    # Find rows where source system is invalid (empty string)
    rejected_source_system = transactions[
        transactions[source_system_column].str.strip() == ''
    ].copy()

    # Record exactly why they failed
    rejected_source_system['rejection_reason'] = (
        'INVALID_' + source_system_column.upper()
    )

    return transactions, rejected_source_system


