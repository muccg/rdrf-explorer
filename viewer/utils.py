import re
import json

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from django.db import ProgrammingError
from django.db import connection

from models import Query
from viewer import app_settings
from rdrf.utils import mongo_db_name_reg_id


class DatabaseUtils(object):

    QUERY_PARAMETERS = [
        "%registry%",
    ]

    def __init__(self, form_object=None):
        if form_object:
            self.form_object = form_object
            self.query = form_object['sql_query'].value()
            self._sql_parameters()
    
    def connection_status(self):
        try:
            client = self._get_mongo_client()
            client.close()
            return True, None
        except ConnectionFailure, e:
            return False, e
    
    def run_sql(self):
        try:
            cursor = connection.cursor()
            self.cursor = cursor.execute(self.query)
            self.result = self._dictfetchall(cursor)
        except ProgrammingError as error:
            self.result = {'error_msg': error.message}

        return self

    def run_mongo(self):
        client = self._get_mongo_client()
        
        projection = {}
        criteria = {}
        
        database = client[mongo_db_name_reg_id(self.form_object['registry'].value())]
        collection = database[self.form_object['collection'].value()]
        
        mongo_search_type = self.form_object['mongo_search_type'].value()
        
        criteria = self._string_to_json(self.form_object['criteria'].value())
        projection = self._string_to_json(self.form_object['projection'].value())
        aggregation = self._string_to_json(self.form_object['aggregation'].value())

        django_ids = []
        for r in self.result:
            django_ids.append(r["id"])

        
        records = []
        if mongo_search_type == 'F':
            criteria["django_id"] = {"$in":django_ids}
            results = collection.find(criteria, projection)
        elif mongo_search_type == 'A':
            if "$match" in aggregation:
                aggregation["$match"].update({"django_id":{"$in":django_ids }})
            else:
                aggregation["$match"] = {"django_id":{"$in":django_ids }}
            results = collection.aggregate([aggregation])
            results = results['result']
    
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
            records.append(row)
        
        self.result = records
        return self

    def run_full_query(self):
        sql_result = self.run_sql().result
        mongo_result = self.run_mongo().result
        
        self.result = []
        for sr in sql_result:
            for mr in mongo_result:
                if sr['id'] == int(mr['django_id']):
                    mr.update(sr)
                    self.result.append(mr)

        return self
    
    def _string_to_json(self, string):
        result = None
        try:
            result = json.loads(string)
        except ValueError:
            result = None
        return result
    
    def _sql_parameters(self):
        for param in self.QUERY_PARAMETERS:
            param_name = re.findall("%(.*?)%", param)[0]
            param_value = self.form_object[param_name].value()
            self.query = self.query.replace(param, param_value)
        
    def _dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
    
    def _get_mongo_client(self):
        return MongoClient(app_settings.VIEWER_MONGO_HOST,
                           app_settings.VIEWER_MONGO_PORT)

