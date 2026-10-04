import importlib

import cleaning
importlib.reload(cleaning)

from cleaning import load_data,clean_customer_id, clean_account_id, clean_datetime
from cleaning import cleaned_amount, currency_code, merchant_id, clean_merchant_name, clean_merchant_category
from cleaning import clean_transaction_type, clean_payment, clean_channel, clean_city, province_state, clean_country, description, clean_source_system
import pandas as pd # type: ignore


transactions = cleaning.load_data('data/raw/transactions_raw.csv')
accounts = cleaning.load_data('data/raw/accounts.csv')
merchants = cleaning.load_data('data/raw/merchants.csv')

transactions_copy = transactions.copy()

transactions_copy = cleaning.clean_customer_id(transactions_copy, accounts)

transactions_copy, rejected_accounts = cleaning.clean_account_id(
    transactions_copy,
    accounts
)

transactions_copy, rejected_datetime = cleaning.clean_datetime(transactions_copy, ['transaction_timestamp', 'ingested_at'])

transactions_copy, rejected_amount = cleaning.cleaned_amount(transactions_copy, 'amount')

transactions_copy, rejected_currency = cleaning.currency_code(transactions_copy, 'currency')

transactions_copy, rejected_merchant = cleaning.merchant_id(transactions_copy, 'merchant_id')

transactions_copy, rejected_merchant_name = cleaning.clean_merchant_name(transactions_copy, merchants) 

transactions_copy, rejected_merchant_category = cleaning.clean_merchant_category(transactions_copy, 'merchant_category') 

transactions_copy, rejected_transaction_type = cleaning.clean_transaction_type(transactions_copy, 'transaction_type')

transactions_copy, rejected_payment_method = cleaning.clean_payment(transactions_copy, 'payment_method')

transactions_copy, rejected_channel = cleaning.clean_channel(transactions_copy, 'channel')

transactions_copy, rejected_city = cleaning.clean_city(transactions_copy, 'city')

transactions_copy = cleaning.province_state(transactions_copy, 'province_state')

transactions_copy, rejected_country = cleaning.clean_country(transactions_copy, 'country')

transactions_copy, rejected_description = cleaning.description(transactions_copy, 'description')

transactions_copy, rejected_source_system = cleaning.clean_source_system(transactions_copy, 'source_system')

print(transactions_copy.info())

pd.concat([rejected_accounts, rejected_datetime, rejected_amount, rejected_currency, rejected_merchant, rejected_merchant_name, rejected_merchant_category, rejected_transaction_type, rejected_payment_method, rejected_channel, rejected_city, rejected_country, rejected_description, rejected_source_system], ignore_index=True)
