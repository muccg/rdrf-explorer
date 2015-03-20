from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.views.generic.base import View
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from viewer import app_settings
from forms import QueryForm
from models import Query
from utils import DatabaseUtils

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


class QueryView(LoginRequiredMixin, View):

    def get(self, request, query_id):
        from rdrf.models import Registry
        
        query_model = Query.objects.get(id=query_id)
        query_form = QueryForm(instance=query_model)
        params = _get_default_params(request, query_form)
        params['edit'] = True
        params['registries'] = Registry.objects.all()
        return render_to_response('viewer/query.html', params)

    def post(self, request, query_id):
        query_model = Query.objects.get(id=query_id)
        query_form = QueryForm(request.POST, instance=query_model)
        form = QueryForm(request.POST)

        database_utils = DatabaseUtils(form)

        if request.is_ajax():
            result = database_utils.run_sql().run_mongo().result
            return HttpResponse(dumps(result))
        else:
            if form.is_valid():
                m = query_form.save(commit=False)
                m.save()
                return redirect(m)


class DownloadQueryView(LoginRequiredMixin, View):

    def get(self, request, query_id):
        query_model = Query.objects.get(id=query_id)
        database_utils = DatabaseUtils()
        
        result = database_utils.run_query(query_model)

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

    def post(self, request):
        form = QueryForm(request.POST)
        database_utils = DatabaseUtils(form)
        results = database_utils.run_sql().result
        response = HttpResponse(dumps(results, default=json_serial))
        return response


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    serial = obj.isoformat()
    return serial


def _get_default_params(request, form):
        database_utils = DatabaseUtils()
        status, error = database_utils.connection_status()

        return RequestContext(request, {
            'version': app_settings.APP_VERSION,
            'host': app_settings.VIEWER_MONGO_HOST,
            'status': status,
            'error_msg': error,
            'form': form,
            'csrf_token_name': app_settings.CSRF_NAME
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
