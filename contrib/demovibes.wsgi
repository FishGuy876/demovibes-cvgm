import os, sys

sys.path.append('__PATH__')
sys.path.append('__PATH__/demovibes')
os.environ['DJANGO_SETTINGS_MODULE'] = 'demovibes.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
