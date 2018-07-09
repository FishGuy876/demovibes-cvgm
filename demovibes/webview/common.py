from webview import models
from webview.models import get_now_playing_song
from webview.decorators import atomic
from django.conf import settings
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseForbidden
from functools import wraps
from django.utils.decorators import available_attrs
from django.template.loader import render_to_string

from django.db.models import Sum

from django.utils.html import escape

import logging
import socket
import datetime
import j2shim

MIN_QUEUE_SONGS_LIMIT = getattr(settings, "MIN_QUEUE_SONGS_LIMIT", 0)
QUEUE_TIME_LIMIT = getattr(settings, "QUEUE_TIME_LIMIT", False)
SELFQUEUE_DISABLED = getattr(settings, "SONG_SELFQUEUE_DISABLED", False)
LOWRATE = getattr(settings, 'SONGS_IN_QUEUE_LOWRATING', False)

def ratelimit(limit=10,length=86400):
    """
    Limit function to <limit> runs per ip address, over <length> seconds.

    Expects first function parameter to be a request object.
    """
    def decorator(func):
        def inner(request, *args, **kwargs):
            ip_hash = str(hash(request.META['REMOTE_ADDR']))
            result = cache.get(ip_hash)
            if result:
                result = int(result)
                if result == limit:
                    return HttpResponseForbidden("Ooops, too many requests!")
                else:
                    cache.incr(ip_hash)
                    return func(request,*args,**kwargs)
            cache.add(ip_hash,1,length)
            return func(request, *args, **kwargs)
        return wraps(func, assigned=available_attrs(func))(inner)
    return decorator

def play_queued(queue_item):
    queue_item.song.times_played = queue_item.song.times_played + 1
    queue_item.song.save()
    queue_item.time_played=datetime.datetime.now()
    queue_item.played = True
    queue_item.save()
    temp = get_now_playing(True)
    temp = get_history(True)
    temp = get_queue(True)
    models.add_event(eventlist=("queue", "history", "nowplaying"))


def find_queue_time_limit(user, song):
    """
    Return seconds left of limit
    """
    next = False
    if QUEUE_TIME_LIMIT:
        limit = models.TimeDelta(**QUEUE_TIME_LIMIT[0])
        duration = models.TimeDelta(**QUEUE_TIME_LIMIT[1])
        start = datetime.datetime.now() - duration

        #Fetch all queued objects by that user in given time period
        Q = models.Queue.objects.filter(requested__gt = start, requested_by = user).order_by("id")

        total_seconds = limit.total_seconds() - song.get_songlength()

        if Q.count():
            queued_seconds = Q.aggregate(Sum("song__song_length"))["song__song_length__sum"] #Length of all songs queued
            seconds_left = total_seconds - queued_seconds
            earliest = Q[0].requested
            next = earliest + duration
            if seconds_left <= 0:
                seconds_left = seconds_left + song.get_songlength()
                return (True, seconds_left, next)
            return (False, seconds_left, next)
        return (False, total_seconds, next)
    return (False, False, next)

@atomic("queue-song")
def queue_song(song, user, event = True, force = False):
    event_metadata = {'song': song.id, 'user': user.id}

    if SELFQUEUE_DISABLED and song.is_connected_to(user):
        models.send_notification("You can't request your own songs!", user)
        return False

    #To update lock time and other stats
    song = models.Song.objects.get(id=song.id)

    key = "songqueuenum-" + str(user.id)

    EVS = []
    Q = False
    time = song.create_lock_time()
    result = True

    if models.Queue.objects.filter(played=False).count() < MIN_QUEUE_SONGS_LIMIT and not song.is_locked():
        force = True

    time_full, time_left, time_next = find_queue_time_limit(user, song)
    time_left_delta = models.TimeDelta(seconds=time_left)

    if not force:

        if time_full:
            result = False
            models.send_notification("Song is too long. Remaining timeslot : %s. Next timeslot change: <span class='tzinfo'>%s</span>" %
                        (time_left_delta.to_string(), time_next.strftime("%H:%M")), user)

        requests = cache.get(key, None)
        Q = models.Queue.objects.filter(played=False, requested_by = user)
        if requests == None:
            requests = Q.count()
        else:
            requests = num(requests)

        if result and requests >= settings.SONGS_IN_QUEUE:

            models.send_notification("You have reached your unplayed queue entry limit! Please wait for your requests to play.", user)
            result = False

        if result and song.is_locked():
            # In a case, this should not append since user (from view) can't reqs song locked
            models.send_notification("Song is already locked", user)
            result = False

        if result and LOWRATE and song.rating and song.rating <= LOWRATE['lowvote']:
            if Q.filter(song__rating__lte = LOWRATE['lowvote']).count() >= LOWRATE['limit']:
                models.send_notification("Anti-Crap: Song Request Denied (Rating Too Low For Current Queue)", user)
                result = False

    if result:
        song.locked_until = datetime.datetime.now() + time
        song.save()
        Q = models.Queue(song=song, requested_by=user, played = False)
        Q.eta = Q.get_eta()
        Q.save()
        EVS.append('a_queue_%i' % song.id)

        #Need to add logic to decrease or delete when song gets played
        #cache.set(key, requests + 1, 600)

        if event:
            bla = get_queue(True) # generate new queue cached object
            EVS.append('queue')
            msg = "%s has been queued." % escape(song.title)
            msg += " It is expected to play at <span class='tzinfo'>%s</span>." % Q.eta.strftime("%H:%M")
            if time_left != False:
                msg += " Remaining timeslot : %s." % time_left_delta.to_string()
            models.send_notification(msg, user)
        models.add_event(eventlist=EVS, metadata = event_metadata)
        return Q


def get_now_playing(create_new=False):
    logging.debug("Getting now playing")
    key = "nnowplaying"

    try:
        songtype = get_now_playing_song(create_new)
        song = songtype.song
    except:
        return ""

    R = cache.get(key)
    if not R or create_new:
        comps = models.Compilation.objects.filter(songs__id = song.id)
        R = j2shim.r2s('webview/t/now_playing_song.html', { 'now_playing' : songtype, 'comps' : comps })
        cache.set(key, R, 300)
        logging.debug("Now playing generated")
    R = R.replace("((%timeleft%))", str(songtype.timeleft()))
    return R

def get_history(create_new=False):
    key = "nhistory"
    logging.debug("Getting history cache")
    R = cache.get(key)
    if not R or create_new:
        nowplaying = get_now_playing_song()
        limit = nowplaying and (nowplaying.id - 50) or 0
        logging.info("No existing cache for history, making new one")
        history = models.Queue.objects.select_related(depth=3).filter(played=True).filter(id__gt=limit).order_by('-time_played')[1:21]
        R = j2shim.r2s('webview/js/history.html', { 'history' : history })
        cache.set(key, R, 300)
        logging.debug("Cache generated")
    return R

def get_oneliner(create_new=False):
    key = "noneliner"
    logging.debug("Getting oneliner cache")
    R = cache.get(key)
    if not R or create_new:
        logging.info("No existing cache for oneliner, making new one")
        lines = getattr(settings, 'ONELINER', 10)
        oneliner = models.Oneliner.objects.select_related(depth=2).order_by('-id')[:lines]
        R = j2shim.r2s('webview/js/oneliner.html', { 'oneliner' : oneliner })
        cache.set(key, R, 600)
        logging.debug("Cache generated")
    return R

def get_roneliner(create_new=False):
    key = "rnoneliner"
    logging.debug("Getting reverse oneliner cache")
    R = cache.get(key)
    if not R or create_new:
        logging.info("No existing cache for reverse oneliner, making new one")
        oneliner = models.Oneliner.objects.select_related(depth=2).order_by('id')[:15]
        R = j2shim.r2s('webview/js/roneliner.html', { 'oneliner' : oneliner })
        cache.set(key, R, 600)
        logging.debug("Cache generated")
    return R

def get_queue(create_new=False):
    key = "nqueue"
    logging.debug("Getting cache for queue")
    R = cache.get(key)
    if not R or create_new:
        logging.info("No existing cache for queue, making new one")
        queue = models.Queue.objects.select_related(depth=2).filter(played=False).order_by('id')
        R = j2shim.r2s("webview/js/queue.html", { 'queue' : queue })
        cache.set(key, R, 300)
        logging.debug("Cache generated")
    return R

def get_profile(user):
    """
    Get a user's profile.

    Tries to get a user's profile, and create it if it doesn't exist.
    """
    try:
        profile = user.get_profile()
    except:
        profile = models.Userprofile(user = user)
        profile.save()
    return profile

def get_latest_event():
    curr = cache.get("curr_event")
    if not curr:
        curr = get_latest_event_lookup()
        cache.set("curr_event", curr, 30)
    return curr

def get_latest_event_lookup():
    try:
        return models.AjaxEvent.objects.order_by ('-id')[0].id
    except:
        return 0

def add_oneliner (user, message):
    message = message.strip()
    can_post = user.is_superuser or not user.has_perm ('webview.mute_oneliner')
    
    r = user.get_profile().is_muted()
    if can_post and r:
        can_post = False
        models.send_notification('You can not post until <span class="tzinfo">%s</span>. Reason: %s' % (r["time"].strftime("%H:%M"), r["reason"]), user)

    if message and can_post:
        models.Oneliner.objects.create (user = user, message = message)
        f = get_oneliner (True)
        models.add_event (event = 'oneliner')

def get_event_key(key):
    event = get_latest_event()
    return "%sevent%s" % (key, event)
