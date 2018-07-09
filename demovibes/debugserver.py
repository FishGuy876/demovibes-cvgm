import os, sys
try:
    from werkzeug import DebuggedApplication, run_simple
except:
    print "Need werkzeug installed to run"


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
SITE_ROOT = os.path.dirname(SITE_ROOT)

sys.path.append(SITE_ROOT)
sys.path.append(os.path.join(SITE_ROOT, "demovibes"))



os.environ['DJANGO_SETTINGS_MODULE'] = 'demovibes.settings'

def null_technical_500_response(request, exc_type, exc_value, tb):
    raise exc_type, exc_value, tb

from django.views import debug
from django.core.handlers.wsgi import WSGIHandler
debug.technical_500_response = null_technical_500_response

application = WSGIHandler()

application = DebuggedApplication(application, True)

# Mount the application to the url
applications = {'/':'application'}

if __name__ == '__main__':

    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    SITE_ROOT = os.path.dirname(SITE_ROOT)

    def pj(*path):
        return os.path.join(SITE_ROOT, *path)

    import sys
    sys.path.append(SITE_ROOT)
    sys.path.append(pj("demovibes"))
    try:
        port = int(sys.argv[1])
    except (ValueError, IndexError):
        port = 8123
    run_simple('0.0.0.0', port, application, True)
