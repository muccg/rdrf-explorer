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

**settings.py config**
VIEWER_MONGO_HOST -> default to 'localhost'

VIEWER_MONGO_PORT -> default to 27017

VIEWER_MONGO_DATABASE = -> default to 'test'
