#!/usr/bin/python

import unittest
import requests
import json
from faker import Faker
from faker.providers import bank,lorem,python

_BASE_URL = "http://faas.192.168.39.31.nip.io"

fake = Faker()
fake.add_provider(bank)
fake.add_provider(python)
fake.add_provider(lorem)

ibans = [ fake.iban() for _ in range(0,3) ]
customers = []

def call_function(service, name, data):
    data_json = json.dumps(data)
    response = requests.get(f"{_BASE_URL}/{service}/{name}", data=data_json)
    response.raise_for_status()
    content = json.loads(response.content)
    if("_error" in content):
        raise Exception("got error: %s" % content["_error"])
    return content

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_customer_create(self):
        for iban in ibans:
            data = {"name": fake.name(), "address": fake.address(), "IBAN": iban}
            result = call_function("customers", "create", data)
            self.assertIn("_id", result)
            customers.append(result)
    
    def test_02_customer_get(self):
        c = customers[0]
        data = {"id": c['_id']}
        result = call_function("customers", "get", data)
        self.assertEqual(result['_id'], c['_id'])
    
    def test_03_customers_get_by(self):
        iban = ibans[0]
        data = {"attr": "IBAN", "value": iban}
        result = call_function("customers", "get-by", data)
        self.assertEqual(result['IBAN'], iban)

    def test_04_customers_delete(self):
        c_id = customers[-1]["_id"]
        data = {"id": c_id}
        result = call_function("customers", "delete", data)
        self.assertEqual(result['_id'], c_id)

    def test_05_transactions_create(self):
        data = {
            "amount": str(fake.pyfloat(positive=True)),
            "creditor_IBAN": ibans[0],
            "debtor_IBAN": ibans[1],
            "description": fake.paragraph(nb_sentences=2)
        }
        result = call_function("transactions", "create", data)
        self.assertIn("execution_date", result)
    
    def test_06_transactions_list(self):
        data = {
            "IBAN": ibans[0]
        }
        result = call_function("transactions", "list", data)
        self.assertGreater(len(result), 0)
    
    def test_07_report_get(self):
        data = {
            "IBAN": ibans[0],
            "month": "2020-03"
        }
        result = call_function("reports", "get", data)
        self.assertEqual(result['customer']['IBAN'], ibans[0])
        self.assertGreater(len(result['transactions']), 0, msg=ibans[0])

    
if __name__ == '__main__':
    unittest.main()
