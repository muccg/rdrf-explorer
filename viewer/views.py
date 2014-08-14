from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.views.generic.base import View
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from viewer import app_settings
from forms import QueryForm
from viewer.utils import connection_status, get_database_names
from viewer.utils import get_collections, run_query
from models import Query

import csv
import json
import urllib2
from bson.json_util import dumps


class LoginRequiredMixin(object):
    @method_decorator(login_required)
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


class QueryView(LoginRequiredMixin, View):

    def get(self, request, query_id):
        query_model = Query.objects.get(id=query_id)
        query_form = QueryForm(instance=query_model)
        params = _get_default_params(request, query_form)
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


class LoadRecordsFromApi(LoginRequiredMixin, View):

    def get(self, request):
        req = urllib2.Request(app_settings.API_URL, None, {'format': 'json'})
        opener = urllib2.build_opener()
        f = opener.open(req)
        results = json.load(f)
        return HttpResponse(dumps(results['objects']))


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
