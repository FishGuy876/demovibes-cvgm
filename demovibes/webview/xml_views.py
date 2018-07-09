from demovibes.webview.models import *
from demovibes.webview.common import get_now_playing_song, ratelimit
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from mybaseview import MyBaseView
from django.views.decorators.cache import cache_page

#
# Note: Only the class based views use jinja templates.
# The rest of the views use standard django templates
#

class XMLView(MyBaseView):
    cache_output = True #If cache key defined, cache the whole output
    content_type = "application/xml"
    basetemplate = 'webview/xml/'

@ratelimit(20, 600) # 20 queries max per 10 minutes (average 1 query per 30 second)
@cache_page(15)
def queue(request):
    try :
        now_playing = get_now_playing_song()
        if now_playing:
            history = Queue.objects.select_related(depth=2).filter(played=True).filter(id__gt=now_playing.id - 50).order_by('-id')[1:21]
        else:
            history = Queue.objects.select_related(depth=2).filter(played=True).order_by('-id')[1:21]
    except IndexError:
        history = []
    queue = Queue.objects.select_related(depth=2).filter(played=False).order_by('id')
    return render_to_response('webview/xml/queue.xml', \
        {'now_playing': now_playing, 'history': history, 'queue': queue}, \
        context_instance=RequestContext(request), mimetype = "application/xml")

def oneliner(request):
    try:
        oneliner_data = Oneliner.objects.select_related(depth=1).order_by('-id')[:20]
    except:
        return "Invalid Oneliner Data"

    return render_to_response('webview/xml/oneliner.xml', \
        {'oneliner_data' : oneliner_data}, \
        context_instance=RequestContext(request), mimetype = "application/xml")

@cache_page(60)
def online(request):
    try:
        timefrom = datetime.datetime.now() - datetime.timedelta(minutes=5)
        online_data = Userprofile.objects.filter(last_activity__gt=timefrom).order_by('user__username')
    #online_data = Userprofile.objects.select_related(depth=2).filter(last_activity__gt=timefrom).order_by('user__username')[1:50]
    except:
        return "Invalid Online Data"

    return render_to_response('webview/xml/online.xml', \
        {'online_data' : online_data}, \
        context_instance=RequestContext(request), mimetype = "application/xml")

class SongInfo(XMLView):
    template = "song.xml"

    def initialize(self):
        songid = self.kwargs.get("songid")
        self.song = get_object_or_404(Song, id = songid)

    def get_cache_key(self):
        return "sic%s%s" % (self.song.id, self.song.last_changed)

    def set_context(self):
        return {'song': self.song}

class ArtistInfo (XMLView):
    template = "artist.xml"

    def initialize (self):
        self.artist = get_object_or_404 (Artist, **self.kwargs)

    def get_cache_key (self):
        return "artist-%s-%s" % (self.artist.id, self.artist.last_updated)

    def set_context(self):
        return {'object': self.artist}

class UserView(XMLView):
    full_info = False

    def initialize(self):
        username = self.kwargs.get("username")
        self.user = get_object_or_404(User, username = username)
        self.userprofile = self.user.get_profile()
        if self.userprofile.visible_to == "A":
            self.full_info = True
        self.context['full_info'] = self.full_info
        self.context['target_user'] = self.user
        self.context['target_user_profile'] = self.userprofile

class UserInfo(UserView):
    template = "user.xml"

class UserFavorites(UserView):
    template = "user_favorites.xml"
