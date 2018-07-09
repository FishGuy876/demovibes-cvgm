from webview.models import *
from webview.forms import *
from webview.common import *
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response

from mybaseview import MyBaseView

from django.utils import simplejson

from haystack.query import SearchQuerySet

from tagging.models import Tag

from django.template import RequestContext
from django.conf import settings
import time, datetime
from django.core.cache import cache
import j2shim
import re
import hashlib


idlist = re.compile(r'^(\d+,)+\d+$')


UWSGI_ID_SECRET = getattr (settings, 'UWSGI_ID_SECRET', False)
NUM_SONG_SEARCH_ITEMS = getattr(settings, 'NUM_SONGS_PER_COMPILATION_SEARCH', 20)


class AjaxView(MyBaseView):
    basetemplate = "webview/js/"


@cache_page (60 * 60 * 24)
@cache_control (max_age = 3600 * 24)
def smileys (request):
    filtered = []
    seen = set ()
    for name, path in settings.SMILEYS:
        if path in seen:
            continue

        seen.add (path)
        filtered.append ((name, path))

    s = simplejson.dumps (filtered)
    return HttpResponse (s, "application/json")


@cache_page (60 * 60 * 24)
@cache_control (max_age = 3600 * 24)
def countrybox (request):
    alpha2list = country_by_code2.keys ()
    alpha2list.sort (lambda a, b: cmp (country_by_code2[a].name, country_by_code2[b].name))

    return j2shim.r2r ('webview/t/countrybox.html',
                       {'alpha2list'   : alpha2list},
                       request)


class LicenseView (AjaxView):
    template = "license.html"

    def set_context (self):
        id = self.kwargs.get ("id")
        lic = SongLicense.objects.get (id = id)

        return {'license': lic}


def songinfo (request):
    def makeinfo (song):
        return {"title"     : song.title,
                "artists"   : song.artist(),
                "id"        : song.id,
                "url"       : song.get_absolute_url(),
                "slength"   : song.get_songlength()}

    songid = request.REQUEST.get("q", "").strip()

    if not songid:
        return HttpResponse('{"error": "Empty input"}')

    if songid.isdigit():
        try:
            S = Song.objects.get (id = songid)
            result = [makeinfo(S)]
            return HttpResponse(simplejson.dumps(result))
        except:
            return HttpResponse('{"error": "No song by that ID"}')

    if idlist.match(songid):
        num = songid.split(",")
        res = []

        for x in num:
            S = Song.objects.get(id=x)
            res.append(makeinfo(S))

        return HttpResponse(simplejson.dumps(res))

    SL = SearchQuerySet ().auto_query (songid).models (Song).load_all ()[:NUM_SONG_SEARCH_ITEMS]
    if not SL:
        return HttpResponse('{"error": "No results found"}')

    data = []
    for S in SL:
        data.append(makeinfo(S.object))

    return HttpResponse(simplejson.dumps(data))


def ping (request, event_id):
    """For updating last_active field before sending to event handler."""

    if getattr(settings, "DISABLE_AJAX", False):
        raise

    get_uid = ""
    if request.user.is_authenticated():
        key = "uonli_%s" % request.user.id
        get_uid = "?uid=%s" % request.user.id

        if UWSGI_ID_SECRET:
            hash = hashlib.sha1("%s.%s" % (request.user.id, UWSGI_ID_SECRET)).hexdigest()
            get_uid = get_uid + "&sign=" + hash

        get = cache.get(key)
        if not get:
            profile = get_profile (request.user)
            profile.last_activity = datetime.datetime.now ()
            profile.set_flag_from_ip (request.META.get ('REMOTE_ADDR'))
            profile.last_ip = request.META["REMOTE_ADDR"]
            profile.save ()
            cache.set (key, "1", 100)

    return HttpResponseRedirect ("/demovibes/ajax/monitor/%s/%s" % (event_id, get_uid))


@cache_control (must_revalidate = True, max_age = 10)
def nowplaying (request):
    song = get_now_playing_song ()

    return j2shim.r2r ('webview/js/now_playing.html',
                       {'now_playing'   : song,
                        'user'          : request.user},
                       request)


@cache_control (must_revalidate = True, max_age = 30)
def history(request):
    return HttpResponse (get_history ())


@cache_control (must_revalidate = True, max_age = 30)
def queue (request):
    return HttpResponse (get_queue ())


def oneliner_submit (request):
    """Responsible for submit of a new message of the oneliner chat."""

    if not request.user.is_authenticated():
        return HttpResponse("NoAuth")

    message = request.POST['Line'].strip()
    add_oneliner (request.user, message)

    return HttpResponse("OK")


def get_tags (request):
    q = request.GET.get('q')
    if q:
        l = []
        t = Tag.objects.filter (name__istartswith = q)[:20]

        for tag in t:
            if tag.items.count():
                l.append("%s - %s song(s)" % (tag.name, tag.items.count ()))

        return HttpResponse ('\n'.join(l))

    return HttpResponse ()


@cache_control (must_revalidate = True, max_age = 30)
def oneliner (request):
    return HttpResponse (get_oneliner ())


@cache_control (must_revalidate = True, max_age = 30)
def songupdate (request, song_id):
    song = Song.objects.get (id = song_id)

    span = ("""<span style="display:none">l</span>""" +
            """<img class="song_tail" src="%slock.png" title="Locked" alt="Locked"/>""")

    return HttpResponse (span % settings.MEDIA_URL)


def words (request, prefix):
    """Used to get completion word candidates for oneliner."""

    extrawords = ['boobies', 'boobietrap', 'nectarine']

    profiles = Userprofile.objects.filter (user__username__istartswith = prefix).order_by("-last_activity")[:20]

    words = [a.user.username for a in profiles ]
    words.extend ( [a.handle for a in Artist.objects.filter (handle__istartswith = prefix)[:20] ] )
    words.extend ( [a.name for a in Group.objects.filter (name__istartswith = prefix)[:20] ] )
    words.extend ( [a for a in extrawords if a.lower().startswith (prefix.lower() ) ] )

    return HttpResponse (",".join (words))


def djrandom_mood (request):
    """Called on request from queue list in order to change mood."""

    if not request.user.has_perm ('webview.change_djrandom_options'):
        return HttpResponse("NoAuth")

    form = DJRandomMoodForm (request.POST)
    if form.is_valid ():
        comment = request.user.username
        DJRandomOptions.mood.set_with_comment (form.get_mood (), comment)
        models.add_event (event = 'djrandom_mood')
    else:
        djrandom_options = DJRandomOptions.snapshot ()
        mood = djrandom_options.mood
        form = DJRandomMoodForm (initial = {'mood' : mood})
        comment = mood.comment

    return HttpResponse (form.get_mood_html (set_by = comment))


def djrandom_avoid_explicit (request):
    """Called on request from queue page in order to change avoid explicit option."""

    if not request.user.has_perm ('webview.change_djrandom_options'):
        return HttpResponse("NoAuth")

    form = DJRandomAvoidExplicitForm (request.POST)
    if form.is_valid ():
        comment = request.user.username
        DJRandomOptions.avoid_explicit.set_with_comment (form.get_avoid_explicit (), comment)
        models.add_event (event = "djrandom_avoid_explicit")
    else:
        djrandom_options = DJRandomOptions.snapshot ()
        avoid_explicit = djrandom_options.avoid_explicit
        form = DJRandomAvoidExplicitForm (initial = {'avoid_explicit' : avoid_explicit})
        comment = avoid_explicit.comment

    return HttpResponse (form.get_avoid_explicit_html (set_by = comment))


#  LocalWords:  uonli slength NoAuth img src slock png boobietrap
#  LocalWords:  oneliner
