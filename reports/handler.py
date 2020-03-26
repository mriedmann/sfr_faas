import sys
import os
import json
import time, datetime, calendar
from decimal import Decimal
import requests

customers_function_url = os.getenv('CUSTOMERS_URL', 'http://faas.192.168.39.31.nip.io/customers')
transactions_function_url = os.getenv('TRANSACTIONS_URL', 'http://faas.192.168.39.31.nip.io/transactions')

def func(func):
    def wrapper(event, context):
        # Parse input
        event['data_obj'] = json.loads(event['data'])
        try:
            result = func(**(event['data_obj']))
        except TypeError as err:
            result = {"_error": "invalid input"}
        except Exception as err:
            result = {"_error": f"crash! {str(err)}"}
        return json.dumps(result)
    return wrapper

def get_customer_by_IBAN(IBAN):
    data = "{\"attr\":\"IBAN\",\"value\":\"%s\"}" % IBAN
    r = requests.get(customers_function_url + "/get-by", data=data)
    r.raise_for_status()
    result = json.loads(r.content)
    
    if ("_error" in result):
        return None
    
    return result

def get_month_timestamps(d):
    _, num_days = calendar.monthrange(d.year, d.month)
    first_day = datetime.date(d.year, d.month, 1)
    last_day = datetime.date(d.year, d.month, num_days)
    return (first_day, last_day)

def get_transactions(IBAN, from_date, to_date):
    data = {"IBAN":str(IBAN)}

    if from_date is not None:
        data["from_date"] = from_date.strftime('%Y-%m-%d')

    if to_date is not None:
        data["to_date"] = to_date.strftime('%Y-%m-%d')

    data_json = json.dumps(data)
    r = requests.get(transactions_function_url + "/list", data=data_json)
    r.raise_for_status()
    result = json.loads(r.content)
    
    return result

@func
def get_report(IBAN, month=None):
    customer = get_customer_by_IBAN(IBAN)
    if (customer is None):
        customer = {"_error": "could not receive customer information"}

    month_first_day = month_last_day = None
    if month is not None:
        try:
            month_date = datetime.datetime.strptime(month, "%Y-%m")
            month_first_day, month_last_day = get_month_timestamps(month_date)
        except Exception as err:
            return {"_error": f"date conversion failed ({err})"}
    
    transactions = get_transactions(IBAN, month_first_day, month_last_day)

    return {"customer": customer, "transactions": transactions}
