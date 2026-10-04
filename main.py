import csv
from functions import create_copy, amount_to_numeric, column_to_datetime
from functions import standardize_string, clean_merchant
import pandas as pd
df = pd.read_csv('data/raw/transactions_raw.csv')

df.head(10)

df_copy = create_copy(df)
print(df_copy)

df_copy['amount'] = amount_to_numeric(df_copy['amount'])
print(df_copy['amount'].dtype)

#working on the date columns
df_copy['transaction_timestamp'] = column_to_datetime(df_copy['transaction_timestamp'])
df_copy['ingested_at'] = column_to_datetime(df_copy['ingested_at'])
df_copy['year_month'] = df_copy['transaction_timestamp'].dt.to_period('M')
df_copy['year'] = df_copy['transaction_timestamp'].dt.year

df_copy['currency'] = standardize_string(df_copy['currency'])
print(df_copy['currency'].dtype)

df_copy['merchant_category'] = clean_merchant(df_copy['merchant_category'])
print(df_copy['merchant_category'].dtype)

pd.set_option('display.max_rows', None)

df_copy = df_copy.dropna(subset=['customer_id'])

df_copy[df_copy['account_id'].isna() & df_copy['customer_id'].duplicated(keep=False)]
df_copy['account_id'] = df_copy['account_id'].fillna(df_copy.groupby('customer_id')['account_id'].transform('first'))
df_copy['account_id'].isna().sum()

df_copy['amount'].fillna(df_copy['amount'].mean(), inplace=True)
df_copy['amount'].isna().sum()

#working on the merchant_name column
df_copy['merchant_name'].fillna(df_copy['description'].str.split('-').str[1].str.strip(), inplace=True) 

#leave this one as empty
df_copy[df_copy['province_state'].isna()]

#good to go
df_copy['record_id'].duplicated().sum()

df_copy[df_copy['transaction_id'].duplicated()]
df_copy[df_copy['transaction_id'] == 'TXN00061233']
#since transaction id has some duplicates and not unique per customer, we create a true_transaction_id by combining customer_id and transaction_id
df_copy['true_transaction_id'] = (df_copy['customer_id'].astype(str) + '_' + df_copy['transaction_id'].astype(str))
df_copy['true_transaction_id'].duplicated().sum()

#customer id can have duplicates since a customer can have multiple transactions
df_copy['customer_id'].duplicated().sum()

#account id can have duplicates since an account can be associated with multiple customers
df_copy['account_id'].duplicated().sum()

#merchant id can have duplicates since multiple transactions can occur at the same merchant
df_copy['merchant_id'].duplicated().sum()

# Identify transactions with negative amounts that are not refunds
condition = (df_copy['amount'] < 0) & (df_copy['transaction_type'] != 'refund')
df_copy.loc[condition, ['customer_id', 'amount', 'payment_method', 'description']]

# Convert negative refund amounts to positive
df_copy.loc[df_copy['transaction_type'] == 'refund', 'amount'] = df_copy.loc[df_copy['transaction_type'] == 'refund', 'amount'].abs()

# Convert non-refund transaction amounts to negative
df_copy.loc[df_copy['transaction_type'] != 'refund', 'amount'] = df_copy.loc[df_copy['transaction_type'] != 'refund', 'amount'] * -1

df_copy['flowtype'] = df_copy['transaction_type'].apply(lambda x: 'inflow' if x == 'refund' else 'outflow')

df_copy.to_csv('data/proccessed/cleaned_data.csv', index=False)