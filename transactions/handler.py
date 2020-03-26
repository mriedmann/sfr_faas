import sys
import os
import couchdb
import json
import time
from datetime import datetime
from decimal import Decimal
import requests

server_url = os.getenv('DB_URL', 'http://192.168.39.31:30918/')
customers_function_url = os.getenv('CUSTOMERS_URL', 'http://faas.192.168.39.31.nip.io/customers')

def db_func(func):
    def wrapper(event, context):
        # Connecting with couchdb Server   
        couch = couchdb.Server(server_url)
        # Creating Database  
        context['db'] = couch['swf_faas']
        # Parse input
        event['data_obj'] = json.loads(event['data'])
        try:
            result = func(context['db'], **(event['data_obj']))
        except TypeError as err:
            result = {"_error": "invalid input"}
        return json.dumps(result)
    return wrapper

def convert_to_timestamp(d):
    return time.mktime(d.timetuple())

def get_current_timestamp():
    d = datetime.now()
    return convert_to_timestamp(d)

def validate_IBAN(IBAN):
    data = "{\"attr\":\"IBAN\",\"value\":\"%s\"}" % IBAN
    r = requests.get(customers_function_url + "/get-by", data=data)
    r.raise_for_status()
    result = json.loads(r.content)
    return not ("_error" in result)

@db_func
def create_transaction(db, amount, creditor_IBAN, debtor_IBAN, description):
    execution_date = get_current_timestamp()

    try:
        _amount = Decimal(amount)
        valid_creditor = validate_IBAN(creditor_IBAN)
        valid_debtor = validate_IBAN(debtor_IBAN)
    except Exception as err:
        return {"_error": str(err)}

    if(valid_creditor and valid_debtor):
        doc = {
            'type': 'transaction',
            'execution_date': execution_date, 
            'amount': f"{_amount}",
            'creditor_IBAN': creditor_IBAN, 
            'debtor_IBAN': debtor_IBAN, 
            'description': description
            }
        db.save(doc)
        return doc
    else:
        return {"_error": "one of the given IBANs is invalid"}

@db_func
def list_transactions(db, IBAN, from_date=None, to_date=None):
    if (from_date is None):
        _from_date = datetime.now().replace(month=1,day=1)
    else:
        _from_date = datetime.strptime(from_date, '%Y-%m-%d')

    if (to_date is None):
        _to_date = datetime.now().replace(month=12,day=31)
    else:
        _to_date = datetime.strptime(to_date, '%Y-%m-%d')

    timespan_days = (_to_date - _from_date).days
    print(timespan_days)
    if (timespan_days < 0):
        return {"_error":"from_date cannot be after to_date"}
    elif (timespan_days > 366):
        return {"_error":"cannot list for more then 366 days"}

    query = {
        'selector': { 
            "execution_date": {
                "$gt": convert_to_timestamp(_from_date), 
                "$lt": convert_to_timestamp(_to_date)
            },
            "$or": [ 
                { "creditor_IBAN": IBAN }, 
                { "debtor_IBAN": IBAN } 
            ]
        }, 
        'fields': [
            '_id','execution_date','amount',
            'creditor_IBAN', 'debtor_IBAN', 
            'description'
        ]
    }
    results = list(db.find(query))
    if len(results) > 0:
        for row in results:
            row['execution_date'] = datetime.utcfromtimestamp(row['execution_date']).strftime('%Y-%m-%d')
        return results
    else:
        return []
