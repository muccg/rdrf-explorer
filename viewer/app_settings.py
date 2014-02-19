from django.conf import settings
from viewer import __version__

VIEWER_MONGO_HOST = getattr(settings, "VIEWER_MONGO_HOST", 'localhost')
VIEWER_MONGO_PORT = getattr(settings, "VIEWER_MONGO_PORT", 27017)
VIEWER_MONGO_DATABASE = getattr(settings, "VIEWER_MONGO_DATABASE", 'test')

APP_VERSION = __version__
