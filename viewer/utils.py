from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from models import Query
from viewer import app_settings
import ast


def connection_status():
    try:
        client = _get_mongo_client()
        client.close()
        return True, None
    except ConnectionFailure, e:
        return False, e


def get_database_names():
    try:
        client = _get_mongo_client()
        return client.database_names(), None
    except ConnectionFailure, e:
        return False, e


def get_collections(database):
    client = _get_mongo_client()
    db = client[database]
    return db.collection_names()


def run_query(query):
    client = _get_mongo_client()

    if isinstance(query, Query):
        db = client[query.database]
        coll = db[query.collection]
        fields_dict = ast.literal_eval(
            _remove_special_chars(query.projection))
        criteria_dict = ast.literal_eval(
            _remove_special_chars(query.criteria))
    else:
        db = client[query.cleaned_data['database']]
        coll = db[query.cleaned_data['collection']]
        fields_dict = ast.literal_eval(
            _remove_special_chars(query.cleaned_data['projection']))
        criteria_dict = ast.literal_eval(
            _remove_special_chars(query.cleaned_data['criteria']))

    results = coll.find(criteria_dict, fields_dict)
    
    strings = []
    
    for cur in results:
        row = {}
        for k in cur:
            if isinstance(cur[k], (list, tuple)):
                tmp = []
                for item in cur[k]:
                    tmp.append(item)
                row[k] = tmp
            else:
                row[k] = str(cur[k])
        strings.append(row)

    return strings

def get_keys_for_collection(database, collection):
    client = _get_mongo_client()
    db = client[database]
    coll = db[collection]
    one_row = coll.find_one({}, {'_id': 0})
    keys = []
    for key in one_row:
        keys.append(key)
    return keys
    

def _remove_special_chars(string):
    return ''.join(string.split())


def _get_mongo_client():
    return MongoClient(app_settings.VIEWER_MONGO_HOST,
                       app_settings.VIEWER_MONGO_PORT)
