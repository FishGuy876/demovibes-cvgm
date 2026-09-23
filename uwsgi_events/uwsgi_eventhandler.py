# --- gevent MUST be patched before bottle is imported ---------------------------------------
# bottle 0.9's Request and Response are `threading.local` SUBCLASSES, bound when bottle is
# imported. uWSGI's <gevent-monkey-patch/> runs only AFTER this module is loaded, so without this
# they stay real thread-locals and EVERY concurrent long-poll greenlet shares ONE response object.
# The ingest POST answers "OK", which sets `Content-Length: 2` on that shared object, and the next
# long-poll to wake is then cut to 2 bytes ("\ne") - live updates arrive as garbage, and nginx logs
# "upstream sent more data than specified in Content-Length header". Found 2026-09-19 on the
# production rehearsal. Patching first makes them greenlet-local. Harmless where gevent is absent
# (uWSGI 0.9.x / ugreen, whose venv has no gevent): the ImportError is swallowed. patch_all() is
# idempotent, so uWSGI's own later patch does no harm.
try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    pass

import uwsgi
import bottle
import threading
import hashlib
import pickle
import random
import time


LOCK = threading.Lock()


# --- uWSGI async compatibility ------------------------------------------
#
# This file is the ONLY reason production is pinned to uWSGI 0.9.5.4. It used
# three APIs that were removed after 0.9.x:
#
#   uwsgi.green_pause(n)            suspend this coroutine for n seconds
#   uwsgi.green_unpause_all()       wake every suspended coroutine at once
#   uwsgi.message_manager_marshal   receive uwsgi-protocol modifier-33 messages
#
# uWSGI 2.x offers async_sleep()/suspend() but has NO broadcast-wake
# primitive, so the wake-on-event behaviour is replaced by short-interval
# polling. Worst-case delivery latency becomes POLL_INTERVAL instead of
# instant, which is invisible next to a long-poll that otherwise waits ~60s.
#
# Both paths are kept so the same file runs under either version, and
# production is not forced to move in lockstep with the clone.
HAS_GREEN = hasattr (uwsgi, 'green_pause')

# gevent gives back the EXACT semantics that were lost: Event.wait(timeout)
# is green_pause(), and Event.set() wakes every waiter at once like
# green_unpause_all() did. No polling, no added latency.
try:
    from gevent.event import Event as _GeventEvent
    WAKE = _GeventEvent()
    HAS_GEVENT = True
except ImportError:
    WAKE = None
    HAS_GEVENT = False

# Last-resort fallback only, used when neither uGreen's python API nor gevent
# is available. Costs up to POLL_INTERVAL of delivery latency.
POLL_INTERVAL = 1


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
    if HAS_GREEN:
        # uWSGI 0.9.x: wake every waiting long-poll immediately.
        uwsgi.green_unpause_all()
    elif HAS_GEVENT:
        # set() releases every waiter; clear() re-arms for the next event.
        WAKE.set()
        WAKE.clear()
    # Otherwise waiters notice within POLL_INTERVAL.

    LOCK.release()


def wait_for_event (current_id, seconds):
    """Suspend this request until a newer event arrives, or `seconds` pass.

    0.9.x suspends once and is woken by green_unpause_all(). 2.x has no such
    wake, so sleep in slices and re-check - same observable behaviour, just
    with up to POLL_INTERVAL of latency.
    """

    if HAS_GREEN:
        uwsgi.green_pause (seconds)
        return

    if HAS_GEVENT:
        # Blocks this greenlet until event_receiver calls WAKE.set(), or the
        # timeout expires. Same shape as green_pause + green_unpause_all.
        WAKE.wait (timeout = seconds)
        return

    # Fallback: poll. NOTE async_sleep()+suspend() was tried here first and
    # did NOT terminate - requests ran past <harakiri> and uWSGI SIGKILLed
    # the whole worker, taking all 800 in-flight requests with it. Keep this
    # branch conservative and bounded by iteration count, not just wall time.
    deadline = time.time() + seconds
    iterations = 0
    while time.time() < deadline and iterations < seconds * 2:
        iterations += 1
        time.sleep (POLL_INTERVAL)

        LOCK.acquire()
        current = event
        LOCK.release()

        if current and current[1] > current_id:
            return


# The uwsgi-protocol transport (modifier1=33, "marshalled messages") exists
# only on 0.9.x. On 2.x this receiver is unreachable, and webview/models.py
# falls back to POSTing /demovibes/ajax/monitor/new/ instead - the same path
# sockulf has always used. send_uwsgi_message is the paired API, so its
# presence is a reliable test for which uWSGI we are running under.
if hasattr (uwsgi, 'send_uwsgi_message'):
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
        #Try to stop all from being "done" and re-request at the same time
        wait_for_event (id, 50 + random.randint(0,20) )

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
