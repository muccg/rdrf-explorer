from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from django.db import connection

from models import Query
from viewer import app_settings
import ast
import re

from rdrf.utils import mongo_db_name_reg_id


class SqlUtils():
    
    QUERY_PARAMETERS = [
        "%registry_id%",
    ]
    
    def run_sql(self, query, params):
        for query_p in self.QUERY_PARAMETERS:
            name = re.findall("%(.*?)%", query_p)[0]
            query = query.replace(query_p, params[name])
        cursor = connection.cursor()
        self.cursor = cursor.execute(query)
        return self.result_list(cursor)

    def run_mongo(self, query):
        sql_results = self.result
        return self.run_query(query)
   
    def result_list(self, cursor):
        self.result = self.dictfetchall(cursor)
        return self

    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        
    def validate_sql(self, query, params):
        self.run_sql(query, params)
        return self.dictfetchall(cursor)

    def run_query(self, query):
        client = self._get_mongo_client()
        
        fields_dict = None
        criteria_dict = {}
        
        coll = "cdes"
        db = client[mongo_db_name_reg_id(query['registry'].value())]
        coll = db[query['collection'].value()]
        criteria_dict = ast.literal_eval(self._remove_special_chars(query['criteria'].value()))
        fields_dict = ast.literal_eval(self._remove_special_chars(query['projection'].value()))
        
        django_ids = []
        for r in self.result:
            django_ids.append(r["id"])

        criteria_dict["django_id"] = {"$in": django_ids}

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
    
    def _remove_special_chars(self, string):
        return ''.join(string.split())
    
    
    def _get_mongo_client(self):
        return MongoClient(app_settings.VIEWER_MONGO_HOST,
                           app_settings.VIEWER_MONGO_PORT)
        

def connection_status():
    try:
        client = MongoClient(app_settings.VIEWER_MONGO_HOST, app_settings.VIEWER_MONGO_PORT)
        client.close()
        return True, None
    except ConnectionFailure, e:
        return False, e
