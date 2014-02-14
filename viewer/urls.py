from django.conf.urls import patterns, url
from viewer.views import MainView

urlpatterns = patterns('',
    url(r'$', MainView.as_view(), name='viewer_main'),
)