from django.conf.urls import patterns, url
from viewer.views import MainView, DbView
from viewer.views import QueryView, NewQueryView
from viewer.views import DeleteQueryView, DownloadQueryView

urlpatterns = patterns(
    '',
    url(r'^db/(?P<database_name>\w+)/?$',
        DbView.as_view(), name='viewer_db'),

    url(r'^query/(?P<query_id>\w+)/?$',
        QueryView.as_view(), name='viewer_query'),
    url(r'^query/download/(?P<query_id>\w+)/?$',
        DownloadQueryView.as_view(), name='viewer_query_download'),
    url(r'^query/delete/(?P<query_id>\w+)/?$',
        DeleteQueryView.as_view(), name='viewer_query_delete'),

    url(r'new$', NewQueryView.as_view(), name='viewer_new'),

    url(r'$', MainView.as_view(), name='viewer_main'),
)
