import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

wsgi = importlib.import_module('wsgi', 'django_app.py')
application = wsgi.app
