from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.views.generic.base import View
from django.template import RequestContext
from django.db import connection
from django.db import ProgrammingError

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from viewer import app_settings
from forms import QueryForm
from viewer.utils import connection_status, get_database_names, get_keys_for_collection
from viewer.utils import get_collections, run_query
from models import Query

import csv
import json
import urllib2
from bson.json_util import dumps
from bson import json_util
from datetime import datetime


class LoginRequiredMixin(object):
    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class MainView(LoginRequiredMixin, View):

    def get(self, request):
        return render_to_response(
            'viewer/query_list.html',
            {'object_list': Query.objects.all()},
            _get_default_params(request, None))


class NewQueryView(LoginRequiredMixin, View):

    def get(self, request):
        params = _get_default_params(request, QueryForm)
        return render_to_response('viewer/query.html', params)

    def post(self, request):
        query_form = QueryForm(request.POST)
        if query_form.is_valid():
            m = query_form.save(commit=False)
            m.save()
            return redirect(m)
        return HttpResponse()


class DeleteQueryView(LoginRequiredMixin, View):

    def get(self, request, query_id):
        query_model = Query.objects.get(id=query_id)
        query_model.delete()
        return redirect('viewer_main')


class DbView(LoginRequiredMixin, View):

    def get(self, request, database_name):
        if database_name != "-1":
            colls = get_collections(database_name)
            json_response = json.dumps(colls)
            return HttpResponse(json_response)


class CollectionView(LoginRequiredMixin, View):

    def get(self, request, database_name, collection_name):
        if collection_name != "-1":
            keys = get_keys_for_collection(database_name, collection_name)
            json_response = json.dumps(keys)
            return HttpResponse(json_response)


class QueryView(LoginRequiredMixin, View):

    def get(self, request, query_id):
        query_model = Query.objects.get(id=query_id)
        query_form = QueryForm(instance=query_model)
        params = _get_default_params(request, query_form)
        params['edit'] = True
        return render_to_response('viewer/query.html', params)

    def post(self, request, query_id):
        query_model = Query.objects.get(id=query_id)
        query_form = QueryForm(request.POST, instance=query_model)
        form = QueryForm(request.POST)

        if request.is_ajax():
            if query_form.has_changed() and form.is_valid():
                result = run_query(form)
            else:
                result = run_query(query_model)
            return HttpResponse(dumps(result))
        else:
            if form.is_valid():
                m = query_form.save(commit=False)
                m.save()
                return redirect(m)


class DownloadQueryView(LoginRequiredMixin, View):

    def get(self, request, query_id):
        query_model = Query.objects.get(id=query_id)
        result = run_query(query_model)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % _get_filename(query_id, request)
        writer = csv.writer(response)

        header = _get_header(result)
        writer.writerow(header)

        for r in result:
            row = _get_content(r, header)
            writer.writerow(row)

        return response


class SqlQueryView(View):
    
    def get(self, request):
        try:
            cursor = connection.cursor()
            query = request.GET['sql-query']
            cursor.execute(query)
            result_list = dictfetchall(cursor)
            response = HttpResponse(dumps(result_list, default=json_serial))
        except ProgrammingError as error:
            response = HttpResponse(dumps({'error_msg': error.message}))

        return response


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    #if isinstance(obj, datetime):
    serial = obj.isoformat()
    return serial


def _get_default_params(request, form):
        status, error = connection_status()

        databases = None
        if status:
            databases, err = get_database_names()

        return RequestContext(request, {
            'version': app_settings.APP_VERSION,
            'host': app_settings.VIEWER_MONGO_HOST,
            'database': app_settings.VIEWER_MONGO_DATABASE,
            'status': status,
            'error_msg': error,
            'databases': databases,
            'form': form
        })


def _get_header(result):
    header = []
    for key in result[0].keys():
        header.append(key)
    return header


def _get_content(result, header):
    row = []
    for h in header:
        row.append(result[h])
    return row


def _get_filename(query_id, request):
    return "query_%s_%s.csv" % (query_id, request.user.username)
