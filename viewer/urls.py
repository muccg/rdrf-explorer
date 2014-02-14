from django.conf.urls import patterns, url
from viewer.views import MainView, DbView, QueryView, NewQueryView, DeleteQueryView

urlpatterns = patterns('',
    url(r'^db/(?P<database_name>\w+)/?$', DbView.as_view(), name='viewer_db'),

    url(r'^query/(?P<query_id>\w+)/?$', QueryView.as_view(), name='viewer_query'),
    url(r'^query/delete/(?P<query_id>\w+)/?$', DeleteQueryView.as_view(), name='viewer_query_delete'),

    url(r'new$', NewQueryView.as_view(), name='viewer_new'),

    url(r'$', MainView.as_view(), name='viewer_main'),
)