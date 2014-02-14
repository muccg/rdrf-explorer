from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from viewer import app_settings
import ast


def connection_status():
    try:
        client = MongoClient(app_settings.VIEWER_MONGO_HOST, app_settings.VIEWER_MONGO_PORT)
        client.close()
        return True, None
    except ConnectionFailure, e:
        return False, e


def get_database_names():
    try:
        client = MongoClient(app_settings.VIEWER_MONGO_HOST, app_settings.VIEWER_MONGO_PORT)
        return client.database_names(), None
    except ConnectionFailure, e:
        return False, e


def get_collections(database):
    client = MongoClient(app_settings.VIEWER_MONGO_HOST, app_settings.VIEWER_MONGO_PORT)
    db = client[database]
    return db.collection_names()


def run_query(query_model):
    client = MongoClient(app_settings.VIEWER_MONGO_HOST, app_settings.VIEWER_MONGO_PORT)
    
    db = client[query_model.database]
    coll = db[query_model.collection]
    fields_dict =  ast.literal_eval(_remove_special_chars(query_model.projection))
    criteria_dict = ast.literal_eval(_remove_special_chars(query_model.criteria))
    
    return coll.find(criteria_dict, fields_dict)

def _remove_special_chars(string):
    return ''.join(string.split())