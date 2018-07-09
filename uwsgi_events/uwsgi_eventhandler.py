import uwsgi
import bottle
import threading
import hashlib
import pickle
import random


LOCK = threading.Lock()


try:
    import local_config
    allowed_ips = getattr(local_config, "ALLOWED_IPS", ["127.0.0.1"])
    debug = getattr(local_config, "DEBUG", False)
    secret = getattr(local_config, "UWSGI_ID_SECRET", None)
except BaseException as exc:
    print "EventHandler: Could not load local settings, using default! Error: " + str (exc)
    debug = False
    secret = None
    allowed_ips = ["127.0.0.1"]

bottle.debug (debug)


event = []


@bottle.post('/demovibes/ajax/monitor/new/')
def http_event_receiver():
    """Serves request sent by HTTP from sockulf."""

    ip = bottle.request.environ.get('REMOTE_ADDR')
    if ip not in allowed_ips:
        print "Rejected IP: " + ip
        return ip

    try:
        data = bottle.request.forms.get('data')
        data = pickle.loads(data)

        event_receiver(data, 0)
    except BaseException as err:
        print "Error handling request through HTTP: " + str (err)

    return "OK"


def event_receiver (obj, id):
    """Used directly by uwsgi to handle events sent by demovibes."""

    LOCK.acquire()

    global event
    event = obj
    uwsgi.green_unpause_all()

    LOCK.release()

uwsgi.message_manager_marshal = event_receiver


@bottle.get ('/demovibes/ajax/monitor/:id#[0-9]+#/')
def handler (id):
    global event

    # Validate user signature
    userid = bottle.request.GET.get ('uid', None)
    if userid and secret:
        hash = hashlib.sha1("%s.%s" % (userid, secret)).hexdigest()
        sign = bottle.request.GET.get ('sign', "NA")
        if hash != sign:
            userid = None

    id = int (id)

    LOCK.acquire()
    myevent = event # We don't want update in a middle...'
    LOCK.release()

    # Event format: (list of events, recent event id)

    # Lets sleep for awhile in case there is no interesting events
    if not myevent or myevent[1] <= id:
        uwsgi.green_pause(50 + random.randint(0,20) ) #Try to stop all from being "done" and re-request at the same time

    LOCK.acquire()
    myevent = event
    LOCK.release()

    # One more try
    if not myevent:
        yield ""
    else:
        eventid = myevent[1]
        levent = [x[1] for x in myevent[0] if x[0] > id and (x[2] == "N" or (userid and x[2] == int(userid)))]
        levent = set(levent)

        #yield "\n".join(levent) + "\n!%s" % eventid
        #yield "eval://Error no id : %s\n" % str(myevent) + "\n".join(levent) + "\n!%s" % eventid
        yield "\n" + "\n".join(levent) + "\n!%s" % eventid


application = bottle.default_app()

#  LocalWords:  EventHandler sockulf uwsgi
