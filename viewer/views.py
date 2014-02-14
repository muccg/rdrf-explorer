from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from viewer import app_settings
from viewer.utils import connection_status


class MainView(View):
    
    def get(self, request):
        params = self._get_default_params()
        return render(request, "viewer/new_query.html", params)


    def _get_default_params(self):
        _params = {
            'version': app_settings.APP_VERSION,
            'host': app_settings.VIEWER_MONGO_HOST,
            'database': app_settings.VIEWER_MONGO_DATABASE,
            'status': connection_status()
        }
        return _params