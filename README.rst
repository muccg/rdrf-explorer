=====================
Django MongoDB Viewer
=====================

*setup.py*

Add to dependency_links:
"https://bitbucket.org/ccgmurdoch/django-mongodb-viewer/downloads/django-mongodb-viewer-0.0.2.tar.gz"

Add to install_requires:
'django-mongodb-viewer==0.0.2'
   
*settings.py*

Add to INSTALLED_APPS:
'viewer'

*urls.py*

url(r'^viewer/', include('viewer.urls'))


**After installation run syncdb**