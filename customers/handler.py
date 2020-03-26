import sys
import os
import io
import hashlib
import couchdb
import json

server_url = os.getenv('DB_URL', 'http://192.168.39.31:30918/')

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

@db_func
def create_customer(db, name, address, IBAN):
    h = hashlib.md5(f"{IBAN}".encode("utf-8")).hexdigest()
    doc = {'_id': h, 'type': 'customer', 'name':name, 'address':address, 'IBAN': IBAN}
    db.save(doc)
    return doc

@db_func
def get_customer(db, id):
    doc = db.get(id, {"_error":"customer does not exist"})
    return doc

@db_func
def get_customer_by(db, attr, value):
    query = {'selector': {f"{attr}": value}, 'fields': ['_id','name','IBAN','address']}
    results = list(db.find(query))
    if len(results) > 0:
        return results[0]
    else:
        return {"_error":"no customer with this attribute found"}

@db_func
def delete_customer(db, id):
    doc = db.get(id)
    if doc is None:
        return {"_error":"user not found"}
    db.delete(doc)
    return {"_id":id}
