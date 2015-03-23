import re
import json

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from django.db import ProgrammingError
from django.db import connection

from models import Query
from viewer import app_settings
from rdrf.utils import mongo_db_name_reg_id
from models import Query
from forms import QueryForm

class DatabaseUtils(object):

    QUERY_PARAMETERS = [
        "%registry%",
    ]

    def __init__(self, form_object=None):
        if form_object and isinstance(form_object, QueryForm):
            self.form_object = form_object
            self.query = form_object['sql_query'].value()
            self.regsitry_id = self.form_object['registry'].value()
            self.collection = self.form_object['collection'].value()
            self.criteria = self._string_to_json(self.form_object['criteria'].value())
            self.projection = self._string_to_json(self.form_object['projection'].value())
            self.aggregation = self._string_to_json(self.form_object['aggregation'].value())
            self.mongo_search_type = self.form_object['mongo_search_type'].value()
            self._sql_parameters(form_object)
        elif form_object and isinstance(form_object, Query):
            self.form_object = form_object
            self.query = form_object.sql_query
            self.regsitry_id = self.form_object.registry.id
            self.collection = self.form_object.collection
            self.criteria = self._string_to_json(self.form_object.criteria)
            self.projection = self._string_to_json(self.form_object.projection)
            self.aggregation = self._string_to_json(self.form_object.aggregation)
            self.mongo_search_type = self.form_object.mongo_search_type
            self._sql_parameters(form_object)
    
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
        
        database = client[mongo_db_name_reg_id(self.regsitry_id)]
        collection = database[self.collection]
        
        mongo_search_type = self.mongo_search_type
        
        criteria = self.criteria
        projection = self.projection
        aggregation = self.aggregation

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
    
    def _sql_parameters(self, form_object):
        for param in self.QUERY_PARAMETERS:
            param_name = re.findall("%(.*?)%", param)[0]
            if isinstance(form_object, QueryForm):
                param_value = form_object[param_name].value()
            elif isinstance(form_object, Query):
                param_value = getattr(form_object, param_name)
            self.query = self.query.replace(param, str(param_value.id))
        
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

