from webview import models as m
from webview import forms as f
from webview import common
from webview.decorators import atomic, cached_method

from openid_provider.models import TrustedRoot

from mybaseview import MyBaseView

from tagging.models import TaggedItem
import tagging.utils

from forum import models as fm

from django.template import Context, loader
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login
from django.db.models import Count, Sum, Avg, Max
from django.db.models import Q as DQ

import logging
import datetime
import j2shim
import hashlib
import re
import random


L = logging.getLogger('webview.views')

class WebView(MyBaseView):
    basetemplate = "webview/"

class SongView(WebView):

    def initialize(self):
        songid = self.kwargs['song_id']
        self.context['song'] = self.song = get_object_or_404(m.Song, id=songid)

class SongAddScreenshot(SongView):
    def GET(self):
        return create_screenshot(self.request, self.song)

class CompilationView(WebView):

    def initialize(self):
        compid = self.kwargs['compilation_id']
        self.context['compilation'] = self.compilation = get_object_or_404(m.Compilation, id=compid)

class CompilationAddScreenshot(CompilationView):

    def GET(self):
        return create_screenshot(self.request, self.compilation)

class ProfileView(WebView):
    def initialize(self):
        username = self.kwargs['user']
        self.user = get_object_or_404(m.User, username = username)
        self.profile = common.get_profile(self.user)

    def check_permissions(self):
        return self.profile.viewable_by(self.request.user)

class ListByLetter(WebView):
    """
    List a model by letter, if given.

    Model need to have "startswith" and letter var need to be "letter"
    """

    model = None
    alphalist_cache_prefix = "ListByLetter-alphalist-"

    desc_function = None

    # Support for that should be included in the template
    list_title = "List"
    letter_url_name = ""
    all_url_name = ""

    def initialize (self):
        query_hexdigest = hashlib.md5 (str(self.get_objects ().query)).hexdigest()
        self.__alphalist_cache_key = self.alphalist_cache_prefix + query_hexdigest
        alphalist = self.get_alphalist ()

        letter = self.kwargs.get ("letter", False)

        if letter and not letter in alphalist or letter == '-':
            letter = '#'

        self.letter = letter
        self.context ['letter'] = letter
        self.context ['al'] = alphalist

    def get_list_title (self):
        return self.list_title

    def get_objects (self):
        return self.model.objects.all()

    def get_alphalist (self):
        @cached_method (key = self.__alphalist_cache_key, timeout = 3)
        def get ():
            return map (lambda x: x['startswith'] == '#' and '-' or x['startswith'],
                        self.get_objects ().distinct().values ('startswith').order_by('startswith'))

        return get ()

    def set_context(self):
        if self.model:
            if self.letter:
                results = self.get_objects().filter (startswith = self.letter)
            else:
                results = self.get_objects()

            return {'object_list'       : results,
                    'list_title'        : self.get_list_title (),
                    'letter_url_name'   : self.letter_url_name,
                    'all_url_name'      : self.all_url_name,
                    'desc_function'     : self.desc_function}

        return {}

class AjaxifyView(WebView):
    redirect_to = "dv-root"

    def GET(self):
        if not self.request.is_ajax():
            self.redirect(self.redirect_to)
        return HttpResponse("")

    def make_ajax_return(self):
        return HttpResponse("You forgot to define 'make_ajax_return', mate!")

    def POST(self):
        if not self.request.user.is_authenticated():
            if self.request.is_ajax():
                return HttpResponse("")
            return self.redirect("/account/signin/")
        songid = self.request.POST.get("songid")
        if songid:
            self.song = m.Song.objects.get(id = songid)

        self.handle_form(self.request.POST)

        if self.request.is_ajax():
            return self.make_ajax_return()

        self.redirect(self.request.META.get('HTTP_REFERER') or self.redirect_to)

def check_muted(request):
    profile = request.user.get_profile()
    muted = profile.is_muted()
    if muted:
        return j2shim.r2r('webview/muted.html', {'muted' : muted}, request)

#-------------------------------------------------------

class ListSmileys(WebView):
    template = "smileys.html"
    def set_context(self):
        return {'smileys': settings.SMILEYS}

class PlaySong(SongView):
    template="playsong.html"

    def check_permissions(self):
        return self.song.downloadable_by(self.request.user)

    def set_context(self):
        limit = None
        if m.CHEROKEE_SECRET:
            key = "urlgenlimit_%s" % self.request.user.id
            number = m.get_cherokee_limit(self.request.user).get("number",0)
            limit = number - cache.get(key, 0)
        self.song.log(self.request.user, "Song preview / download")
        return {'song': self.song, 'limit': limit}

class AddCompilation(WebView):
    template = "add_compilation.html"
    login_required = True
    forms = [
        (f.CreateCompilationForm, "compform"),
    ]

    action = "created"

    def pre_view(self):
        self.context['songsinput']=""

    def save_compilation(self, compdata, songs):
        newcf = compdata.save(commit=False)
        if not newcf.id:
            newcf.created_by = self.request.user
            newcf.status = "U"
        newcf.last_updated = datetime.datetime.now() # Fixes bug of new compilations not appearing in Recent Updates
        newcf.save()
        compdata.save_m2m()

        artists = []
        playtime = 0
        newcf.reset_songs()
        for index, S in enumerate(songs):
            newcf.add_song(S, index)
            playtime = playtime + S.get_songlength()
            for a in S.get_metadata().artists.all():
                if a not in artists:
                    artists.append(a)
        newcf.running_time = playtime
        newcf.prod_artists.clear()
        for a in artists:
            newcf.prod_artists.add(a)
        newcf.save()
        newcf.log(self.request.user, "Compilation %s" % self.action)
        return newcf

    def POST(self):
        songstr = self.request.POST.get("songsinput", "").split(",")
        self.context['songsinput'] = self.request.POST.get("songsinput", "")
        songs = []
        if songstr:
            for S in songstr:
                # By default songsinput is empty but in fact we have one entry in list (u'')
                # So the code will goes here ... but not valid S
                if S:
                    songs.append(m.Song.objects.get(id=S))

        if self.forms_valid and songs:
            newcf = self.save_compilation(self.context["compform"], songs)
            self.redirect(newcf)

class EditCompilation(AddCompilation):
    staff_required = True
    action = "edited"

    def form_compform_init(self):
        ci = self.kwargs.get("comp_id")
        self.c = m.Compilation.objects.get(id=ci)
        return {'instance': self.c}

    def post_view(self):
        if not self.context['songsinput']:
            songs = self.c.get_songs()
            self.context['songsinput'] = ','.join([ str(s.id) for s in songs ])

def about_pages(request, page):
    try:
        return direct_to_template(request, template="about/%s.html" % page)
    except TemplateDoesNotExist:
        return HttpResponseNotFound()

@login_required
def inbox(request):
    pms = request.GET.get('type','')
    delete = request.GET.get('delete','')
    if delete:
        try:
            delpm = int(delete)
            pm = m.PrivateMessage.objects.get(pk = delpm, to = request.user)
        except:
            return HttpResponseNotFound()
        pm.visible = False
        pm.save()
    if pms == "sent":
        mails = m.PrivateMessage.objects.filter(sender = request.user, visible = True)
    else:
        pms = "received" #to remove injects
        mails = m.PrivateMessage.objects.filter(to = request.user, visible = True)
    return j2shim.r2r('webview/inbox.html', {'mails' : mails, 'pms': pms}, request=request)

@login_required
def read_pm(request, pm_id):
    pm = get_object_or_404(m.PrivateMessage, id = pm_id)
    if pm.to == request.user:
        pm.unread = False
        pm.save()
        return j2shim.r2r('webview/view_pm.html', {'pm' : pm}, request=request)
    if pm.sender == request.user:
        return j2shim.r2r('webview/view_pm.html', {'pm' : pm}, request=request)
    return HttpResponseRedirect(reverse('dv-inbox'))

@login_required
def send_pm(request):
    r = check_muted(request)
    if r: 
        return r

    if request.method == 'POST':
        form = f.PmForm(request.POST)
        if form.is_valid():
            F = form.save(commit=False)
            F.sender=request.user
            F.save()
            m.send_notification("%s sent you a <a href='%s'>message</a> with title '%s'" % (escape(F.sender.username), F.get_absolute_url(), escape(F.subject)), F.to)
            return HttpResponseRedirect(reverse('dv-inbox'))
    else:
        title = request.GET.get('title', "")
        to = request.GET.get('to', "")
        try:
            U = m.User.objects.get(username=to)
        except:
            U = None
        form = f.PmForm(initial= {'to': U, 'subject' : title})
    return j2shim.r2r('webview/pm_send.html', {'form' : form}, request)

class addComment(SongView):
    """
    Add a comment to a song.
    """
    login_required = True

    def pre_view(self):
        self.redirect(self.song)

    def POST(self):
        r = check_muted(self.request)
        if r: return r

        comment = self.request.POST.get("Comment", "").strip()
        if comment:
            m.SongComment.objects.create(comment = comment, song = self.song, user = self.request.user)
            if getattr(settings, "NOTIFY_NEW_SONG_COMMENT", False):
                m.send_notification("%s commented on the song <a href='%s'>%s</a>" % (escape(self.request.user.username), self.song.get_absolute_url(), escape(self.song.title)), None, 2)

def site_about(request):
    """
    Support for a generic 'About' function
    """
    return j2shim.r2r('webview/site-about.html', { }, request)

def chat(request):
    """
        Support for a generic 'chat' page
    """
    return j2shim.r2r('webview/chat.html', { }, request)


class ListQueue(WebView):
    """
    Display the current song, the next songs in queue, and the latest 20 songs in history.
    Also provides a way to view DJRandom mood.
    """

    template = "queue_list.html"

    def set_context(self):
        # DJRandom status - - - - - - -  --
        djrandom_options = m.DJRandomOptions.snapshot ()
        mood = djrandom_options.mood
        avoid_explicit = djrandom_options.avoid_explicit

        mood_form = f.DJRandomMoodForm (initial = {'mood' : mood})
        mood_html = mood_form.get_mood_html (set_by = mood.comment)

        ae_form = f.DJRandomAvoidExplicitForm (initial = {'avoid_explicit' : avoid_explicit})
        ae_html = ae_form.get_avoid_explicit_html (set_by = avoid_explicit.comment)

        return {'djrandom_mood_html'                    : mood_html,
                'djrandom_mood_field_html'              : mood_form.get_mood_field_html (),
                'djrandom_avoid_explicit_html'          : ae_html,
                'djrandom_avoid_explicit_field_html'    : ae_form.get_avoid_explicit_field_html (),
                'now_playing'                           : "",
                'history'                               : common.get_history(),
                'queue'                                 : common.get_queue(),
        }

# Slightly modified template of list_songs, to show songs via year
def list_year(request, year_id):
    songs = m.Song.active.filter (songmetadata__active = True, songmetadata__release_year = year_id).order_by('title')
    
    params = {
        'object_list' : songs,
        'year' : year_id,
        'letter_url_name' : "dv-year"
    }
    
    return j2shim.r2r ('webview/year_list.html', params, request)
    
def list_song(request, song_id):
    song = get_object_or_404 (m.Song, id = song_id)

    # Simple queries, it is expected that they are evaluated from inside the template only
    # .. otherwise cache is quite useless. Just try to keep it simple here
    comps = m.Compilation.objects.filter (songs__id = song.id)
    remixes = m.Song.active.filter (songmetadata__active = True, songmetadata__remix_of_id = song.id)

    def calc_tag_cloud ():
        tags = m.Tag.objects.filter (id__in = song.tags).annotate (count = Count ("items"))
        return tagging.utils.calculate_cloud (tags)

    params = {
        'object' : song,
        'vote_range': [1, 2, 3, 4, 5],
        'comps' : comps,
        'remixes' : remixes,
        'related_f': (lambda: m.Song.tagged.related_to (song, num = 5)),
        'tags_f': calc_tag_cloud
    }

    return j2shim.r2r ('webview/song_detail.html', params, request)

# This can probbably be made a generic object
def list_screenshot(request, screenshot_id):
    screenshot = get_object_or_404(m.Screenshot, id=screenshot_id)
    return j2shim.r2r('webview/screenshot_detail.html', { 'object' : screenshot }, request)

class ViewUserFavs(ProfileView):
    """
    List the favorites of a user
    """
    template = "user_favorites.html"

    def set_context(self):
        favorites = m.Favorite.objects.filter(user = self.user)
        return {'favorites':favorites, 'favuser': self.user}

class MyProfile(WebView):
    template = "my_profile.html"
    login_required = True
    forms = [(f.ProfileForm, "form")]

    def initialize(self):
        self.profile = common.get_profile(self.request.user)
        if self.profile.have_artist():
            self.context['lic'] = f.LicenseForm()
        self.links = LinkCheck("U", object = self.profile)

    def pre_view(self):
        rootid = self.request.REQUEST.get("killroot", False)
        if rootid and rootid.isdigit():
            root = TrustedRoot.objects.get(id=rootid)
            if root.openid.user == self.request.user:
                root.delete()
                return self.redirect("dv-my_profile")

    def handle_artistedit(self):
        L = f.LicenseForm(self.request.POST)
        if L.is_valid():
            artist = self.request.user.artist
            lic = L.cleaned_data['license']
            for song in artist.get_songs():
                song.log(self.request.user, "License Mass Change to %s" % lic)
                song.license = lic
                song.save()
            self.redirect("dv-my_profile")

    def POST(self):
        if self.profile.have_artist() and self.request.POST.get("artistdata"):
            self.handle_artistedit()
        elif self.forms_valid and self.links.is_valid(self.request.POST):
            self.context['form'].save()
            self.links.save(self.profile)
            self.redirect("dv-my_profile")

    def form_form_init(self):
        return {'instance': self.profile}

    def set_context(self):
        return {'profile': self.profile, 'links': self.links}


class ViewProfile(ProfileView):
    """
    View a user's profile
    """
    template = "view_profile.html"

    def set_context(self):
        return {'profile': self.profile}

def search(request):
    """
    Return the first 40 matches of songs, artists and groups.
    """
    if request.method == 'POST' and "Search" in request.POST:
        searchterm = request.POST['Search']
        result_limit = getattr(settings, 'SEARCH_LIMIT', 40)
        if settings.USE_FULLTEXT_SEARCH == True:
            users = m.User.objects.filter(username__search = searchterm)[:result_limit]
            songs = m.Song.objects.select_related(depth=1).filter(title__search = searchterm)[:result_limit]
            artists = m.Artist.objects.filter(handle__search = searchterm)|m.Artist.objects.filter(name__search = searchterm)[:result_limit]
            groups = m.Group.objects.filter(name__search = searchterm)[:result_limit]
            compilations = m.Compilation.objects.filter(name__search = searchterm)[:result_limit]
            labels = m.Label.objects.filter(name__search = searchterm)[:result_limit]
        else:
            users = m.User.objects.filter(username__icontains = searchterm)[:result_limit]
            songs = m.Song.objects.select_related(depth=1).filter(title__icontains = searchterm)[:result_limit]
            artists = m.Artist.objects.filter(handle__icontains = searchterm)|m.Artist.objects.filter(name__icontains = searchterm)[:result_limit]
            groups = m.Group.objects.filter(name__icontains = searchterm)[:result_limit]
            compilations = m.Compilation.objects.filter(name__icontains = searchterm)[:result_limit]
            labels = m.Label.objects.filter(name__icontains = searchterm)[:result_limit]


        return j2shim.r2r('webview/search.html', \
            { 'songs' : songs, 'artists' : artists, 'groups' : groups, 'users' : users, 'compilations' : compilations, 'labels' : labels }, \
            request=request)
    return j2shim.r2r('webview/search.html', {}, request=request)

def show_approvals(request):
    """
    Shows the most recently approved songs in it's own window
    """
    result_limit = getattr(settings, 'UPLOADED_SONG_COUNT', 150)
    songs = m.SongApprovals.objects.order_by('-id')[:result_limit]

    return j2shim.r2r('webview/recent_approvals.html', { 'songs': songs , 'settings' : settings }, request=request)

class ListArtists(ListByLetter):
    template = "artist_list.html"
    model = m.Artist
    list_title = "Complete Artist List"
    letter_url_name = "dv-artists_letter"
    all_url_name = "dv-artists"

class ListGroups(ListByLetter):
    template = "group_list.html"
    model = m.Group

class ListLabels(ListByLetter):
    template = "label_list.html"
    model = m.Label

class ListComilations(ListByLetter):
    template = "compilation_list.html"
    model = m.Compilation
    list_title = "Complete Compilation / Album / Production List"
    letter_url_name = "dv-compilations_letter"
    all_url_name = "dv-compilations"

class ListSongs(ListByLetter):
    template = "song_list.html"
    model = m.Song
    list_title = "List Of Songs"
    letter_url_name = "dv-songs_letter"
    all_url_name = "dv-songs"

class ListScreenshots(ListByLetter):
    template = "screenshot_list.html"
    model = m.Screenshot
    list_title = "Gallery Of Images"
    letter_url_name = "dv-screenshots_letter"
    all_url_name = "dv-screenshots"

    def get_objects(self):
        return self.model.objects.filter(status="A")

class ThemeClass(WebView):
    def initialize(self):
        themeid = self.kwargs['theme_id']
        self.context['theme'] = self.theme = get_object_or_404(m.Theme, id=themeid)

class ThemeInfo(ThemeClass):
    template = "theme_details.html"

class ThemeEdit(ThemeClass):
    template = "theme_edit.html"
    forms = [(f.ThemeForm, "form")]
    login_required = True

    def form_form_init(self):
        return {'instance': self.theme}

    def POST(self):
        if self.forms_valid and self.request.user == self.theme.creator:
            self.context['form'].save()
            self.redirect(self.context['theme'])

class ThemeAddImage(ThemeClass):
    def GET(self):
        if self.request.user == self.theme.creator:
            return create_screenshot(self.request, self.theme)
        self.redirect("/")

class ThemeList(WebView):
    template = "themes_list.html"

    def get_objects(self):
        q = m.Theme.objects.filter (active=True)
        q = q.annotate (user_count = Count("userprofile"))

        # Add user who didn't care to select a theme
        themeless = m.Userprofile.objects.filter (theme = None).count ()
        if themeless:
            default_theme = m.Theme.objects.all().order_by("-default")
            if default_theme:
                default_theme = default_theme[0]
                for t in q:
                    if t.id == default_theme.id:
                        t.user_count += themeless

        return q

    def POST(self):
        id = int(self.request.POST.get("theme_id"))
        theme = m.Theme.objects.get(id=id)
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            p.theme = theme
            p.save()
        self.redirect("dv-themelist")

    def set_context(self):
        return {"themes": self.get_objects() }

@login_required
def log_out(request):
    """
    Show a user a form, and then logs user out if a form is sent in to that address.
    """
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect("/")
    return j2shim.r2r('webview/logout.html', {}, request=request)

class songHistory(SongView):
    """
    List queue history of song
    """
    template = "song_history.html"
    def set_context(self):
        return {'requests': self.song.queue_set.all()}

class songVotes(SongView):
    """
    List vote history of song
    """
    template = "song_votes.html"
    def set_context(self):
        return {'votelist': self.song.songvote_set.all()}

class songComments(SongView):
    """
    List the comments belonging to a song
    """
    template = "song_comments.html"
    def set_context(self):
        return {'commentlist': self.song.songcomment_set.all()}

def view_compilation(request, comp_id):
    """
    Try to view a compilation entry.
    """
    permission = request.user.has_perm("webview.make_session")
    comp = get_object_or_404(m.Compilation, id=comp_id) # Find it, or return a 404 error

    if permission:
        sessionform = f.CreateSessionForm()
    else:
        sessionform = False
    if request.method == "POST" and permission:
        sessionform = f.CreateSessionForm(request.POST)
        if sessionform.is_valid():
            desc = sessionform.cleaned_data['description']
            playtime = sessionform.cleaned_data['time']
            for song in comp.get_songs():
                m.Queue.objects.create(song=song, played=False, playtime=playtime, requested_by = request.user, description = desc)
            common.get_queue(True)
            return redirect("dv-queue")
    return j2shim.r2r('webview/compilation.html',
        { 'comp' : comp, 'user' : request.user , 'sessionform': sessionform},
        request=request)

class OnelinerHistorySearch(WebView):
    template = "oneliner_search.html"
    forms = [(f.OnelinerHistory, "form")]
    results = []
    staff_required = True

    def POST(self):
        if self.forms_valid:
            r = m.Oneliner.objects.all()
            data = self.context["form"].cleaned_data
            user = data["username"]
            if user:
                user = m.User.objects.get(username=user)
                r = r.filter(user=user)
            start = data["start"]
            num = data["results"]
            self.results = r[start:num+start]

    def set_context(self):
        return {"results": self.results}

def oneliner(request):
    oneliner = m.Oneliner.objects.select_related(depth=1).order_by('-id')[:20]
    return j2shim.r2r('webview/oneliner.html', {'oneliner' : oneliner}, \
        request=request)

@login_required
def oneliner_submit(request):
    """
    Add a text line to the oneliner.
    Returns user to referrer position, or to /
    """
    message =  request.POST.get('Line').strip()
    common.add_oneliner(request.user, message)
    try:
        refer = request.META['HTTP_REFERER']
        return HttpResponseRedirect(refer)
    except:
        return HttpResponseRedirect("/")

@login_required
def list_favorites(request):
    """
    Display a user's favorites.
    """
    user = request.user
    songs = m.Favorite.objects.filter(user=user)

    try:
        user_profile = m.Userprofile.objects.get(user = user)
        use_pages = user_profile.paginate_favorites
    except:
        # In the event it bails, revert to pages hehe
        use_pages = True

    if(use_pages):
        paginator = Paginator(songs, settings.PAGINATE)
        page = int(request.GET.get('page', '1'))
        try:
            songlist = paginator.page(page)
        except (EmptyPage, InvalidPage):
            songlist = paginator.page(paginator.num_pages)
        return j2shim.r2r('webview/favorites.html', \
          {'songs': songlist.object_list, 'page' : page, 'page_range' : paginator.page_range}, \
          request=request)

    return j2shim.r2r('webview/favorites.html', { 'songs': songs }, request=request)

class QueueSong(AjaxifyView):
    redirect_to = "dv-queue"

    def handle_form(self, form):
        self.r = common.queue_song(self.song, self.request.user)

    def make_ajax_return(self):
        if self.r:
            return HttpResponse("""<span style="display:none">l</span>
                <img class="song_tail" src="%slock.png" title="Locked" alt="Locked"/>""" %
                settings.MEDIA_URL)
        return HttpResponse("")

class ChangeFavorite(AjaxifyView):
    redirect_to = "dv-favorites"

    def handle_form(self, form):
        P = form.get

        if P("change") == "remove":
            Q = m.Favorite.objects.filter(user = self.request.user, song = self.song)
            for x in Q:
                x.delete() # For running Favorite.delete() logic
            m.send_notification("Song removed from your favorites", self.request.user)
        if P("change") == "add":
            try:
                m.Favorite.objects.create(user = self.request.user, song = self.song)
                m.send_notification("Song added to your favorites", self.request.user)
            except:
                pass

    def make_ajax_return(self):
        s = "{{ display.favorite(song, user) }}"
        c = {'song': self.song, 'user': self.request.user}
        return HttpResponse(j2shim.render_string(s, c))

class VoteSong(AjaxifyView):
    redirect_to = "dv-root"

    @atomic("vote")
    def handle_form(self, form):
        self.int_vote = int(form.get("vote", form.get("ajaxvote")))
        if self.int_vote <= 5 and self.int_vote > 0:
            self.song.set_vote(self.int_vote, self.request.user)

    def make_ajax_return(self):
        s = "{{ display.song_vote(song, value) }}"
        c = {'song': self.song, 'value': self.int_vote}
        return HttpResponse(j2shim.render_string(s, c))

class LinkCheck(object):
    def __init__(self, linktype, object = None, status = 0, user = None, add=False):
        self.type = linktype
        self.add = add
        self.verified = []
        self.user = user
        self.status = status
        self.object = object
        self.valid = False
        self.get_list()
        self.title = "External Resources"

    def get_link_for(self, o, generic):
        if not o or not generic:
            return None
        bla = ContentType.objects.get_for_model(o)
        r = m.GenericLink.objects.filter(content_type__pk=bla.id, object_id=o.id, link=generic)
        return r and r[0] or None

    def get_list(self):
        self.linklist = m.GenericBaseLink.objects.filter(linktype = self.type)
        r = []
        for x in self.linklist:
            val = self.get_link_for(self.object, x)
            value=val and val.value or ""
            r.append({'link': x, 'value': value, "error": "", "comment": ""})
        self.links = r
        return self.linklist

    def __unicode__(self):
        return self.as_table()

    def as_table(self):
        """
        Print links form as table
        """
        return j2shim.r2s('webview/t/linksform.html', \
            {'links': self.links, 'title': self.title })

    def is_valid(self, postdict):
        """
        Check if given links are valid according to given regex
        """
        self.valid = True
        for entry in self.links:
            l = entry['link'] # GenericBaseLink object
            key = "LL_%s" % l.id
            if postdict.has_key(key):
                val = postdict[key].strip()
                if val:
                    ckey = key+"_comment"
                    comment = postdict.has_key(ckey) and postdict[ckey].strip() or ""

                    #Fill out dict in case it needs to be returned to user
                    entry['value'] = val
                    entry['comment'] = comment

                    if re.match(l.regex + "$", val):
                        self.verified.append((l, val, comment)) #Add to approved list
                    else:
                        self.valid = False
                        entry['error'] = "The input did not match expected value"
                else:
                    self.verified.append((l, "", "")) #No value for this link
        return self.valid

    def save(self, obj):
        """
        Save links to database
        """
        if self.verified and self.valid:
            for l, val, comment in self.verified:
                r = self.get_link_for(obj, l)
                if val:

                    if r and not self.add:
                        r.value = val
                        r.save()
                    else:
                        m.GenericLink.objects.create(
                            content_object=obj,
                            value=val,
                            link=l,
                            status = self.status,
                            comment = comment,
                            user = self.user
                        )
                else:
                    if r and not self.add:
                        r.delete()
            obj.save() # For caching

@permission_required('webview.change_songmetadata')
def new_songinfo_list(request):
    alink = request.GET.get("alink", False)
    status = request.GET.get("status", False)
    if alink and status.isdigit():
        link = get_object_or_404(m.GenericLink, id=alink)
        link.status = int(status)
        link.content_object.save()
        link.save()
    nusonginfo = m.SongMetaData.objects.filter(checked=False).order_by('added') # Oldest info events will be shown first
    nulinkinfo = m.GenericLink.objects.filter(status=1)
    c = {'metainfo': nusonginfo, 'linkinfo': nulinkinfo}
    return j2shim.r2r("webview/list_newsonginfo.html", c, request)

@permission_required('webview.change_songmetadata')
def list_songinfo_for_song(request, song_id):
    song = get_object_or_404(m.Song, id=song_id)
    metalist = m.SongMetaData.objects.filter(song=song)
    c = {'metalist':metalist, 'song': song}
    return j2shim.r2r("webview/list_songinfo.html", c, request)

@login_required
def add_songlinks(request, song_id):
    song = get_object_or_404(m.Song, id=song_id)
    links = LinkCheck("S", status=1, user = request.user, add = True)
    if request.method == "POST":
        if links.is_valid(request.POST):
            links.save(song)
            return redirect(song)
    c = {'song': song, 'links': links}
    return j2shim.r2r("webview/add_songlinks.html", c, request)


@permission_required('webview.change_songmetadata')
def view_songinfo(request, songinfo_id):
    meta = get_object_or_404(m.SongMetaData, id=songinfo_id)
    post_ok = getattr(settings, 'ADMIN_EMAIL_ON_INFO_APPROVE', False) # Do we send an email on info approve?

    if request.method == "POST":
        if request.POST.has_key("activate") and request.POST["activate"]:
            if post_ok :
                if not meta.checked and meta.user:
                    meta.user.get_profile().send_message(
                        subject="Song info approved",
                        message="Your metadata for song [song]%s[/song] is now active :)"  % meta.song.id,
                        sender = request.user
                    )
            meta.song.log(request.user, "Approved song metadata")
            meta.set_active()
        if request.POST.has_key("deactivate") and request.POST["deactivate"]:
            if not meta.checked and meta.user:
                meta.user.get_profile().send_message(
                    subject="Song info not approved",
                    message="Your metadata for song [song]%s[/song] was not approved :(" % meta.song.id,
                    sender = request.user
                )
            meta.checked = True
            meta.song.log(request.user, "Rejected metadata %s" % meta.id)
            meta.save()
    c = {'meta': meta }
    return j2shim.r2r("webview/view_songinfo.html", c, request)

#Not done
class editSonginfo(SongView):
    template = "edit_songinfo.html"
    forms = [f.EditSongMetadataForm, "form"]
    login_required = True

    def form_form_init(self):
        if self.method == "POST":
            meta = m.SongMetaData(song=self.song, user=self.request.user)
        else:
            meta = self.song.get_metadata()
            meta.comment = ""
        return {'instance': meta}

    def POST(self):
        if self.forms_valid:
            self.context['form'].save()
            self.redirect(self.context['song'])

@login_required
def edit_songinfo(request, song_id):
    song = get_object_or_404(m.Song, id=song_id)
    meta = song.get_metadata()
    meta.comment = ""

    form2 = False
    if (request.user.get_profile().have_artist() and request.user.artist in meta.artists.all()) or (request.user.is_staff):
        form2 = f.SongLicenseForm(instance=song)

    if request.method == "POST":
        meta = m.SongMetaData(song=song, user=request.user)
        if form2 and request.POST.get("special") == "licchange":
            form2 = f.SongLicenseForm(request.POST, instance=song)
            if form2.is_valid():
                s = form2.save()
                song.log(request.user, "Changed song license to %s" % s.license)
                return redirect(song)
        else:
            form = f.EditSongMetadataForm(request.POST, instance=meta)
            if form.is_valid():
                form.save()
                return redirect(song)
    else:
        form = f.EditSongMetadataForm(instance=meta)

    c = {'form': form, 'song': song, 'form2': form2}
    return j2shim.r2r("webview/edit_songinfo.html", c, request)

@login_required
def upload_song(request, artist_id):
    # Check to see if Uploading is currently disabled
    DisableUploads = getattr(settings, 'DISABLE_UPLOADS', False)
    if DisableUploads:
        # Uploads are currently disabled in the system
        return HttpResponseRedirect(reverse('dv-queue'))
    
    artist = get_object_or_404(m.Artist, id=artist_id)
    auto_approve = getattr(settings, 'ADMIN_AUTO_APPROVE_UPLOADS', 0)
    artist_auto_approve = getattr(settings, 'ARTIST_AUTO_APPROVE_UPLOADS', 1)

    links = LinkCheck("S", user = request.user)

    # Quick test to see if the artist is currently active. If not, bounce
    # To the current queue!
    if artist.status != 'A':
        return HttpResponseRedirect(reverse('dv-queue'))

    if request.method == 'POST':
        if artist_auto_approve and artist.link_to_user == request.user:
            # Auto Approved Song. Set Active, Add to Recent Uploads list
            status = 'A'
        else:
            status = 'U'

        # Check to see if moderation settings allow for the check
        if request.user.is_staff and auto_approve == 1:
            # Automatically approved due to Moderator status
            status = 'A'

        a = m.Song(uploader = request.user, status = status)

        form = f.UploadForm(request.POST, request.FILES, instance = a)
        infoform = f.SongMetadataForm(request.POST)

        if links.is_valid(request.POST) and form.is_valid() and infoform.is_valid():
            new_song = form.save(commit=False)
            new_song.save()

            songinfo = infoform.save(commit=False)
            songinfo.user = request.user
            songinfo.song = new_song
            songinfo.checked = True
            songinfo.save()

            infoform.save_m2m()
            form.save_m2m()

            songinfo.artists.add(artist)

            songinfo.set_active()

            links.save(new_song)

            if(new_song.status == 'A'):
                # Auto Approved!
                try:
                    # If the song entry exists, we shouldn't care
                    exist = m.SongApprovals.objects.get(song = new_song)

                except:
                    # Should throw when the song isn't found in the DB
                    Q = m.SongApprovals(song = new_song, approved_by=request.user, uploaded_by=request.user)
                    Q.save()

            return HttpResponseRedirect(new_song.get_absolute_url())
    else:
        form = f.UploadForm()
        infoform = f.SongMetadataForm()
    return j2shim.r2r('webview/upload.html', \
        {'form' : form, 'infoform': infoform, 'artist' : artist, 'links': links }, \
        request=request)

@permission_required('webview.change_song')
def activate_upload(request):
    if "song" in request.GET and "status" in request.GET:
        songid = int(request.GET['song'])
        status = request.GET['status']
        song = m.Song.objects.get(id=songid)
        url = m.Site.objects.get_current()

        if status == 'A':
            stat = "Accepted"
            song.status = "A"
            song.log(request.user, "Approved song")
        if status == 'R':
            stat = "Rejected"
            song.status = 'R'
            song.log(request.user, "Rejected song")

        # This used to be propriatary, it is now a template. AAK
        mail_tpl = loader.get_template('webview/email/song_approval.txt')
        c = Context({
                'songid' : songid,
                'song' : song,
                'site' : m.Site.objects.get_current(),
                'stat' : stat,
                'url' : url,
        })
        song.save()

        # Only add if song is approved! Modified to check to see if song exists first!
        # There is probbably a better way of doing this crude check! AAK
        if(status == 'A'):
            try:
                # If the song entry exists, we shouldn't care
                exist = m.SongApprovals.objects.get(song = song)

            except:
                # Should throw when the song isn't found in the DB
                Q = m.SongApprovals(song=song, approved_by=request.user, uploaded_by=song.uploader)
                Q.save()
            if getattr(settings, "NOTIFY_NEW_SONG_APPROVED", False):
                m.send_notification("Song <a href='%s'>%s</a> was accepted and is now avaliable for queuing!" % (
                    song.get_absolute_url(),
                    escape(song.title),
                ), None, 2)
        if song.uploader.get_profile().pm_accepted_upload and status == 'A' or status == 'R':
            song.uploader.get_profile().send_message(
                sender = request.user,
                message = mail_tpl.render(c),
                subject = "Song Upload Status Changed To: %s" % stat
            )
    songs = m.Song.objects.filter(status = "U").order_by('added')
    return j2shim.r2r('webview/uploaded_songs.html', {'songs' : songs}, request=request)


def showRecentChanges(request):
    # Get some default stat values
    artist_limit = getattr(settings, 'RECENT_ARTIST_VIEW_LIMIT', 20)
    song_limit = getattr(settings, 'RECENT_SONG_VIEW_LIMIT', 20)
    label_limit = getattr(settings, 'RECENT_LABEL_VIEW_LIMIT', 20)
    group_limit = getattr(settings, 'RECENT_GROUP_VIEW_LIMIT', 20)
    comp_limit = getattr(settings, 'RECENT_COMP_VIEW_LIMIT', 20)

    # Make a list of stuff needed for the stats page
    songlist = m.Song.objects.order_by('-songmetadata__added')[:song_limit]
    artistlist = m.Artist.objects.order_by('-last_updated')[:artist_limit]
    labellist = m.Label.objects.order_by('-last_updated')[:label_limit]
    grouplist = m.Group.objects.order_by('-last_updated')[:group_limit]
    complist = m.Compilation.objects.order_by('-last_updated')[:comp_limit]

    # And now return this as a template. default page cache is 5 minutes, which is ample enough
    # To show real changes, without stressing out the SQL loads
    return j2shim.r2r('webview/recent_changes.html', {'songs' : songlist, 'artists' : artistlist, 'groups' : grouplist,
      'labels' : labellist, 'compilations' : complist}, request=request)


class UsersOverview (WebView):
    template = "users_overview.html"

    def set_context (self):
        limit = 50

        country_stats_q = m.User.objects.values ("userprofile__country")
        country_stats_q = country_stats_q.annotate (count = Count("pk"))
        country_stats_q = country_stats_q.order_by ('-count', "userprofile__country")

        by_votes_q = m.User.objects.values ("username", 'userprofile__country')
        by_votes_q = by_votes_q.annotate (count = Count("songvote"), avg = Avg('songvote__vote'))
        by_votes_q = by_votes_q.order_by ('-count')
        by_votes_q = by_votes_q [:limit]

        by_oneliner_q = m.User.objects.values ("username", 'userprofile__country')
        by_oneliner_q = by_oneliner_q.annotate (count = Count("oneliner"))
        by_oneliner_q = by_oneliner_q.order_by ('-count')
        by_oneliner_q = by_oneliner_q [:limit]

        by_uploads_q = m.SongApprovals.objects.values ("uploaded_by__username", 'uploaded_by__userprofile__country')
        by_uploads_q = by_uploads_q.annotate (count = Count("pk"))
        by_uploads_q = by_uploads_q.order_by ('-count')
        by_uploads_q = by_uploads_q [:limit]

        by_tagging_q = m.TagHistory.objects.values ("user__username", 'user__userprofile__country')
        by_tagging_q = by_tagging_q.annotate (count = Count("pk"))
        by_tagging_q = by_tagging_q.order_by ('-count')
        by_tagging_q = by_tagging_q [:limit]

        by_requester_q = m.Queue.objects.values ("requested_by__username", 'requested_by__userprofile__country')
        by_requester_q = by_requester_q.annotate (count = Count("pk"), avg = Avg ("song__rating"))
        by_requester_q = by_requester_q.order_by ('-count')
        by_requester_q = by_requester_q [:limit]

        by_comments_q = m.SongComment.objects.values ("user__username", 'user__userprofile__country')
        by_comments_q = by_comments_q.annotate (count = Count("pk"))
        by_comments_q = by_comments_q.order_by ('-count')
        by_comments_q = by_comments_q [:limit]

        by_posts_q = fm.Post.objects.values ("author__username", 'author__userprofile__country')
        by_posts_q = by_posts_q.annotate (count = Count("pk"))
        by_posts_q = by_posts_q.order_by ('-count')
        by_posts_q = by_posts_q [:limit]

        # We can return queries, since they are lazy. It is supposed that access is cached in html
        return {'by_votes_q'            : by_votes_q,
                'by_oneliner_q'         : by_oneliner_q,
                'by_requester_q'        : by_requester_q,
                'by_comments_q'         : by_comments_q,
                'by_posts_q'            : by_posts_q,
                'by_tagging_q'          : by_tagging_q,
                'by_uploads_q'          : by_uploads_q,
                'country_stats_q'       : country_stats_q}


class RadioOverview (WebView):
    # This is supposed to be cached both on HTML level (to avoid overheads on HTML rendering)
    # and on code level to avoid set_context method overheads

    template = "radio_overview.html"

    @cached_method (key = "RadioOverview-get_total_played_length", timeout = 60)
    def get_total_played (self):
        q = m.Song.active.extra (
                    select = {"total_played_length" : "sum(song_length * times_played)",
                              "total_times_played"  : "sum(times_played)"})
        return list (q.values ("total_played_length", "total_times_played")) [0]

    @cached_method (key = "RadioOverview-stats_by_status", timeout = 60)
    def list_stats_by_status (self):
        return self.__list_grouped_by (m.Song.objects, 'status')

    @cached_method (key = "RadioOverview-votes_by_status", timeout = 60)
    def list_votes_stats (self):
        return self.__list_grouped_by (m.Song.active, 'rating_votes', limit = 6)

    @cached_method (key = "RadioOverview-source_stats", timeout = 60)
    def list_source_stats (self):
        type_by_id = {None : m.Struct (title = "----------------")}
        for type in m.SongType.objects.all():
            type_by_id [type.id] = type

        stats = self.__list_grouped_by (m.Song.active.filter (songmetadata__active = True),
                                        'songmetadata__type')
        for stat in stats:
            stat ['source'] = type_by_id [stat['songmetadata__type']].title

        return stats

    @cached_method (key = "RadioOverview-country_stats", timeout = 86400)
    def list_country_stats (self):
        return self.__list_grouped_by (
            m.Song.active.filter (songmetadata__active = True),
            'songmetadata__artists__home_country',
            order_by = ['-count', 'songmetadata__artists__home_country'])

    @cached_method (key = "RadioOverview-set_context", timeout = 60)
    def set_context (self):
        # Overview
        stats_by_status = self.list_stats_by_status ()
        total_songs = 0
        total_length = 0
        unlocked_songs = 0
        unlocked_length = 0
        status_dict = dict (m.Song.STATUS_CHOICES)
        for stat in stats_by_status:
            stat ['status'] = status_dict [stat ['status']]
            total_songs += stat ['count']
            total_length += stat ['total_playtime']
            unlocked_songs += stat ['unlocked_count']
            unlocked_length += stat ['unlocked_playtime']

        # Result
        return {'vote_stats'                : self.list_votes_stats (),
                "stats_by_status"           : stats_by_status,
                "source_stats"              : self.list_source_stats (),
                "country_stats"             : self.list_country_stats (),
                'total_length'              : total_length,
                'total_songs'               : total_songs,
                'unlocked_length'           : unlocked_length,
                'unlocked_songs'            : unlocked_songs,
                'total_played'              : self.get_total_played ()}

    def __list_grouped_by (self, qmanager, field, limit = None, order_by = None):
        # It is hard or impossible to write that with current django without issuing two queries
        # because django doesn't support expressions in annotations...

        def qfiltered (f = None):
            q = qmanager
            if f:
                q = q.filter (f)
            q = q.values (field)
            q = q.annotate (count = Count("pk"), total_playtime = Sum('song_length'))

            if order_by:
                q = q.order_by (*order_by)
            else:
                q = q.order_by (field)

            if limit:
                return q [:limit]
            else:
                return q.all ()

        # Get total
        by_field = {}
        stats = qfiltered ()
        
        for stat in stats:
            by_field [stat[field]] = stat
            stat ['unlocked_count'] = 0
            stat ['unlocked_playtime'] = 0

        # Mix-in playable stats
        for pstat in qfiltered (m.Song.unlocked_condition()):
            fieldv = pstat [field]
            if fieldv in by_field:
                stat = by_field [fieldv]
                stat ['unlocked_count'] = pstat ['count']
                stat ['unlocked_playtime'] = pstat ['total_playtime']

        # Force evaluation, otherwise django's cache doesn't cache it at all! :E
        return list (stats)


class RadioStatus(WebView):
    template = "stat_songs.html"

    def list_favorites(self):
        return m.Song.objects.order_by('-num_favorited')

    def list_voted(self):
        limit = getattr(settings, "RADIO_STATUS_VOTED_MIN_VOTES", 1)
        return m.Song.objects.filter(rating_votes__gt = limit - 1).order_by('-rating','-rating_votes')

    def list_leastvotes (self):
        return m.Song.objects.filter (m.Song.unlocked_condition ()).order_by ('rating_votes', '?')[:100]

    def list_forgotten (self):
        q = m.Song.active.filter (m.Song.unlocked_condition ())
        q = q.annotate (last_requested = Max("queue__requested"))
        q = q.order_by ('last_requested')
        q = q[:100]
        return q

    def list_random(self):
        max_id = m.Song.objects.order_by('-id')[0].id
        max_songs = m.Song.objects.filter(status="A").count()
        num_songs = 100
        num_songs = num_songs < max_songs and num_songs or max_songs
        songlist = []
        r_done = []
        r = random.randint(0, max_id+1)
        while len(songlist) < num_songs:
          r_list = []
          curr_count = (num_songs - len(songlist) + 2)
          for x in range(curr_count):
            while r in r_done:
              r = random.randint(0, max_id+1)
            r_list.append(r)
          r_done.extend(r_list)
          songlist.extend([s for s in m.Song.objects.filter(id__in=r_list, status="A")])
        return songlist

    def list_mostvotes(self):
        return m.Song.objects.order_by('-rating_votes')

    def list_queued2(self):
        return m.Song.objects.filter(m.Song.unlocked_condition()).order_by('times_played', 'locked_until')

    def list_queued(self):
        return m.Song.objects.filter(status="A").order_by('-times_played')

    def initialize(self):
        self.stats = {
            'random': ("A selection of random songs from the database!",
                       "rating_votes",
                       "# Votes",
                       self.list_random),

            'leastvotes': ("Songs with the least number of votes in the database.",
                           "rating_votes",
                           "# Votes",
                           self.list_leastvotes),

            'forgotten': ("Songs which have not been played in a long time (or not al all).",
                          "times_played",
                          "# Plays",
                          self.list_forgotten),

            'favorites': ("Songs which appear on more users favourite lists.",
                          "num_favorited",
                          "# Faves",
                          self.list_favorites),

            'voted': ("The highest rated songs in the database.",
                      "rating",
                      "Rating",
                      self.list_voted),

            'queued': ("The most played songs in the database.",
                       "times_played",
                       "# Plays",
                       self.list_queued),

            'unplayed': ("The least played songs in the database.",
                         "times_played",
                         "# Plays",
                         self.list_queued2),

            'mostvotes': ("Songs with the highest number of votes cast.",
                          "rating_votes",
                          "# Votes",
                          self.list_mostvotes),
        }

        self.stattype = self.kwargs.get("stattype", "")

    def set_context(self):
        if self.stattype in self.stats.keys():
            title, stat, name, songs = self.stats[self.stattype]
            return {'songs': songs()[:100],
                    'title': title,
                    'numsongs': 100,
                    'stat': stat,
                    'name': name}

        self.template = "radio_status.html"
        return {'keys' : self.stats}


class HelpusWithArtists (ListArtists):
    list_title = "Artists with incorrect/missing information"
    letter_url_name = "dv-helpus-artist_letter"
    all_url_name = "dv-helpus-artist"

    condition = ~DQ (home_country__in = m.country_codes2, status = 'A')
    condition |= DQ (artist_pic = '', status = 'A')

    def get_objects (self):
        return self.model.objects.filter (self.condition)

    def desc_function (self, artist):
        """Describe what is wrong with an artist."""

        problems = []

        if artist.status == 'A':
            country_lc = artist.home_country.lower()
            if country_lc == "":
                problems.append (_("no country"))
            elif country_lc not in m.country_codes2:
                problems.append (_("unknown country (" + artist.home_country + ")"))

            if artist.artist_pic == "":
                problems.append (_("no picture"))

        if problems:
            problems = ", ".join (problems)
            problems = problems[0].upper() + problems[1:]
            return " - " + problems + "."
        else:
            # WTF? why are we here then?
            return ""


class HelpusWithSongs (ListSongs):
    list_title = "Songs with problems"
    letter_url_name = "dv-helpus-song_letter"
    all_url_name = "dv-helpus-song"

    # Kaput
    condition = DQ (status = 'K')

    # Active but no compilation
    condition |= DQ (status = 'A',
                     compilationsonglist = None,
                     songmetadata__active = True,
                     songmetadata__type__compilation_expected = True)

    # No source (song type)
    condition |= DQ (status = 'A',
                     songmetadata__type = None,
                     songmetadata__active = True)

    def get_objects (self):
        q = self.model.objects.filter (self.condition)
        q = q.annotate (comps_count = Count("compilationsonglist__pk"))

        # I hate that but until it is not django 1.4 we can't do better
        q = q.extra (select = {'compilation_expected' : '`webview_songtype`.`compilation_expected`',
                               'songtype'             : '`webview_songtype`.`id`'})

        return q

    def desc_function (self, song):
        """Describe what is wrong with an artist."""

        problems = []

        if song.status == 'K':
            problems.append ("bad status")

        if song.compilation_expected and song.comps_count == 0 and song.status == 'A':
            problems.append ("no compilations")

        if song.status == 'A' and song.songtype == None:
            problems.append ("no source")

        if problems:
            problems = ", ".join (problems)
            problems = problems[0].upper() + problems[1:]
            return problems
        else:
            # WTF? why are we here then?
            return ""


class HelpusWithComps (ListComilations):
    list_title = "Compilations with problems"
    letter_url_name = "dv-helpus-comp_letter"
    all_url_name = "dv-helpus-comp"

    def get_objects (self):
        # That is the only way.. ;( Django's contenttype magic inserts content_type_id=29 into where clause
        # making it impossible to filter screenshots=None, so we have to use inner join
        active_and_with_image_q = self.model.objects.filter (status = 'A', screenshots__image__status = 'A')

        # Active and without an image
        condition = DQ (status = 'A') & ~DQ (pk__in = active_and_with_image_q)

        # Active and no songs (messed up via admin interface or songs are deleted...)
        condition |= DQ (status = 'A', songs = None)

        q = self.model.objects.filter (condition)
        q = q.annotate (screenshots_count = Count("screenshots"),
                        songs_count = Count ("songs"))

        return q

    def desc_function (self, comp):
        """Describe what is wrong with the compilation."""

        problems = []

        if comp.status == 'A':
            if comp.screenshots_count == 0:
                problems.append (_("no cover image"))

            if comp.songs_count == 0:
                problems.append (_("no songs"))

        if problems:
            problems = ", ".join (problems)
            problems = problems[0].upper() + problems[1:]
            return " - " + problems + "."
        else:
            # WTF? why are we here then?
            return ""


class HelpusWithScreenshots (ListScreenshots):
    list_title = "Images with problems"
    letter_url_name = "dv-helpus-screenshot_letter"
    all_url_name = "dv-helpus-screenshot"

    # Connected to nothing
    condition = DQ (status = 'A', screenshotobjectlink = None)

    def get_objects (self):
        q = self.model.objects.filter (self.condition)
        q = q.annotate (slink_count = Count("screenshotobjectlink"))

        return q

    def desc_function (self, scr):
        """Describe what is wrong with the screenshot."""

        problems = []

        if scr.status == 'A':
            if scr.slink_count == 0:
                problems.append (_("connected to nothing"))

        if problems:
            problems = ", ".join (problems)
            problems = problems[0].upper() + problems[1:]
            return " - " + problems + "."
        else:
            # WTF? why are we here then?
            return ""


class TagCloud(WebView):
    template = "tag_cloud.html"
    cache_key = "tag_cloud"
    cache_duration = 24*60*60

    def get_cache_key(self):
        tag_id = cache.get("tagver", 0)
        key = "tag_cloud_%s" % tag_id
        return key

    def set_cached_context(self):
        min_count = getattr(settings, 'TAG_CLOUD_MIN_COUNT', 1)
        tags = m.Song.tags.cloud(min_count=min_count)
        return {'tags': tags}

class MuteOneliner(WebView):
    template = "oneliner_mute.html"
    forms = [
        (f.MuteOnelinerForm, "banform"),
    ]

    def check_permissions(self):
        return self.request.user.has_perm("webview.add_mute_oneliner")

    def POST(self):
        if self.forms_valid:
            data = self.context["banform"].cleaned_data
            user = data["username"]
            endtime = datetime.datetime.now() + datetime.timedelta(minutes=data["mute_minutes"])
            entry = m.OnelinerMuted(
                user=user,
                muted_to=endtime,
                reason=data["reason"],
                added_by=self.request.user,
                details=data["details"],
            )
            if data["ban_ip"]:
                profile = user.get_profile()
                if profile.last_ip:
                    entry.ip_ban = profile.last_ip

            entry.save()
            if getattr(m.settings, "BAN_ANNOUNCE", False):
                m.send_notification("User '%s' have been silenced for %s minutes. Reason: %s" % (user.username,data["mute_minutes"], data["reason"]), None)

            user.get_profile().log(self.request.user, "Silenced for %s minutes. Reason: %s" % (data["mute_minutes"], data["reason"]))
            self.redirect("dv-muteoneliner")

    def set_context(self):
        active = m.OnelinerMuted.objects.filter(muted_to__gt=datetime.datetime.now())
        history = m.OnelinerMuted.objects.filter(muted_to__lt=datetime.datetime.now())[:10]
        return {"active": active, "history": history}

class TagDetail(WebView):
    template = "tag_detail.html"
    cache_duration = 24 * 60 * 60

    def get_cache_key(self):
        tag_id = cache.get ("tagver", 0)
        key = "tagdetail_%s_%s" % (self.kwargs.get("tag", ""), tag_id)

        return hashlib.md5(key).hexdigest()

    def set_cached_context(self):
        tag = self.kwargs.get ("tag", "")

        songs = TaggedItem.objects.get_by_model (m.Song, tag)
        related = m.quickly_get_related_tags (songs,
                                              exclude_tags_str = tag,
                                              limit_to_model = m.Song,
                                              count = True)
        related = tagging.utils.calculate_cloud (related)

        return {'songs'     : songs,
                'related'   : related,
                'tag'       : tag}

class TagEdit(SongView):
    login_required=True
    template = "tag_edit.html"

    def POST(self):
        t = self.request.POST.get('tags', "")
        self.song.tags = re.sub(r'[^a-zA-Z0-9!_\-?& ]+', '', t)
        self.song.log(self.request.user, "Edited tags")
        self.song.save() # For updating the "last changed" value
        m.TagHistory.objects.create(user=self.request.user, song=self.song, tags = self.request.POST['tags'])
        try:
            cache.incr("tagver")
        except:
            cache.set("tagver", 1)
        return self.redirect(self.song)

    def set_context(self):
        tags = tagging.utils.edit_string_for_tags(self.song.tags)
        changes = m.TagHistory.objects.filter(song=self.song).order_by('-id')[:5]
        return {'tags': tags, 'changes': changes}

@login_required
def create_artist(request):
    """
    Simple form to allow registereed users to create a new artist entry.
    """
    auto_approve = getattr(settings, 'ADMIN_AUTO_APPROVE_ARTIST', 0)

    links = LinkCheck("A")

    if request.method == 'POST':
        # Check to see if moderation settings allow for the check
        if request.user.is_staff and auto_approve == 1:
            # Automatically approved due to Moderator status
            status = 'A'
        else:
            status = 'U'

        a = m.Artist(created_by = request.user, status = status)
        form = f.CreateArtistForm(request.POST, request.FILES, instance = a)
        if form.is_valid() and links.is_valid(request.POST):
            new_artist = form.save(commit=False)
            new_artist.save()
            form.save_m2m()

            links.save(new_artist)

            return HttpResponseRedirect(new_artist.get_absolute_url())
    else:
        form = f.CreateArtistForm()
    return j2shim.r2r('webview/create_artist.html', \
        {'form' : form, 'links': links }, \
        request=request)

@permission_required('webview.change_artist')
def activate_artists(request):
    """
    Shows the most recently added artists who have a 'U' status in their upload marker
    """
    if "artist" in request.GET and "status" in request.GET:
        artistid = int(request.GET['artist'])
        status = request.GET['status']
        artist = m.Artist.objects.get(id=artistid)
        url = m.Site.objects.get_current()  # Pull this into a variable

        if status == 'A':
            stat = "Accepted"
            artist.log(request.user, "Activated artist")
            artist.status = "A"
        if status == 'R':
            stat = "Rejected"
            artist.log(request.user, "Rejected artist")
            artist.status = 'R'

        # Prepare a mail template to inform user of the status of their request
        mail_tpl = loader.get_template('webview/email/artist_approval.txt')
        c = Context({
                'artist' : artist,
                'site' : m.Site.objects.get_current(),
                'stat' : stat,
                'url' : url,
        })
        artist.save()

        # Send the email to inform the user of their request status

        if artist.created_by.get_profile().email_on_artist_add and status == 'A' or status == 'R':
            artist.created_by.get_profile().send_message(sender = request.user,
                message = mail_tpl.render(c),
                subject = u"Artist %s : %s" % (artist.handle, stat)
            )

    artists = m.Artist.objects.filter(status = "U").order_by('last_updated')
    return j2shim.r2r('webview/pending_artists.html', { 'artists': artists }, request=request)

@login_required
def create_group(request):
    """
    Simple form to allow registereed users to create a new group entry.
    """
    auto_approve = getattr(settings, 'ADMIN_AUTO_APPROVE_GROUP', 0)

    links = LinkCheck("G")

    if request.method == 'POST':
        # Check to see if moderation settings allow for the check
        if request.user.is_staff and auto_approve == 1:
            # Automatically approved due to Moderator status
            status = 'A'
        else:
            status = 'U'

    if request.method == 'POST':
        g = m.Group(created_by = request.user, status = status)
        form = f.CreateGroupForm(request.POST, request.FILES, instance = g)
        if form.is_valid() and links.is_valid(request.POST):
            new_group = form.save(commit=False)
            new_group.save()
            form.save_m2m()

            links.save(new_group)

            return HttpResponseRedirect(new_group.get_absolute_url())
    else:
        form = f.CreateGroupForm()
    return j2shim.r2r('webview/create_group.html', \
        {'form' : form, 'links': links }, \
        request=request)

@permission_required('webview.change_group')
def activate_groups(request):
    """
    Shows the most recently added groups who have a 'U' status in their upload marker
    """
    if "group" in request.GET and "status" in request.GET:
        groupid = int(request.GET['group'])
        status = request.GET['status']
        group = m.Group.objects.get(id=groupid)

        if status == 'A':
            stat = "Accepted"
            group.status = "A"
        if status == 'R':
            stat = "Rejected"
            group.status = 'R'

        # Prepare a mail template to inform user of the status of their request
        mail_tpl = loader.get_template('webview/email/group_approval.txt')
        c = Context({
                'group' : group,
                'site' : m.Site.objects.get_current(),
                'stat' : stat,
        })
        group.save()

        # Send the email to inform the user of their request status
        if group.created_by.get_profile().email_on_group_add and status == 'A' or status == 'R':
            group.created_by.get_profile().send_message(
                sender = request.user,
                message = mail_tpl.render(c),
                subject = "Group Request Status Changed To: %s" % stat
            )

    groups = m.Group.objects.filter(status = "U").order_by('last_updated')
    return j2shim.r2r('webview/pending_groups.html', { 'groups': groups }, request=request)

@permission_required('webview.change_compilation')
def activate_compilations(request):
    """
    Shows the most recently added compilations who have a 'U' status in their upload marker
    """
    if "compilation" in request.GET and "status" in request.GET:
        compilationid = int(request.GET['compilation'])
        status = request.GET['status']
        compilation = m.Compilation.objects.get(id=compilationid)

        if status == 'A':
            stat = "Accepted"
            compilation.status = "A"
        if status == 'R':
            stat = "Rejected"
            compilation.status = 'R'

        # Prepare a mail template to inform user of the status of their request
        mail_tpl = loader.get_template('webview/email/compilation_approval.txt')
        c = Context({
                'compilation' : compilation,
                'site' : m.Site.objects.get_current(),
                'stat' : stat,
        })
        compilation.save()

        # Send the email to inform the user of their request status
        if compilation.created_by.get_profile().email_on_group_add and status == 'A' or status == 'R':
            compilation.created_by.get_profile().send_message(
                sender = request.user,
                message = mail_tpl.render(c),
                subject = "Compilation Request Status Changed To: %s" % stat
            )

    compilations = m.Compilation.objects.filter(status = "U").order_by('last_updated')
    return j2shim.r2r('webview/pending_compilations.html', { 'compilations': compilations }, request=request)

@login_required
def create_label(request):
    """
    Simple form to allow registereed users to create a new label entry.
    """
    auto_approve = getattr(settings, 'ADMIN_AUTO_APPROVE_LABEL', 0)

    links = LinkCheck("L")

    if request.method == 'POST':
        # Check to see if moderation settings allow for the check
        if request.user.is_staff and auto_approve == 1:
            # Automatically approved due to Moderator status
            status = 'A'
        else:
            status = 'U'

    if request.method == 'POST':
        l = m.Label(created_by = request.user, status = status)
        form = f.CreateLabelForm(request.POST, request.FILES, instance = l)
        if form.is_valid() and links.is_valid(request.POST):
            new_label = form.save(commit=False)
            new_label.save()
            form.save_m2m()

            links.save(new_label)

            return HttpResponseRedirect(new_label.get_absolute_url())
    else:
        form = f.CreateLabelForm()
    return j2shim.r2r('webview/create_label.html', \
        {'form' : form, 'links': links }, \
        request=request)

@permission_required('webview.change_label')
def activate_labels(request):
    """
    Shows the most recently added labels who have a 'U' status in their upload marker
    """
    if "label" in request.GET and "status" in request.GET:
        labelid = int(request.GET['label'])
        status = request.GET['status']
        this_label = m.Label.objects.get(id=labelid)

        if status == 'A':
            stat = "Accepted"
            this_label.status = "A"
        if status == 'R':
            stat = "Rejected"
            this_label.status = 'R'

        # Prepare a mail template to inform user of the status of their request
        mail_tpl = loader.get_template('webview/email/label_approval.txt')
        c = Context({
                'label' : this_label,
                'site' : m.Site.objects.get_current(),
                'stat' : stat,
        })
        this_label.save()

        # Send the email to inform the user of their request status
        if this_label.created_by.get_profile().email_on_group_add and status == 'A' or status == 'R':
            this_label.created_by.get_profile().send_message(
                sender = request.user,
                message = mail_tpl.render(c),
                subject = "Label Request Status Changed To: %s" % stat
            )

    labels = m.Label.objects.filter(status = "U").order_by('last_updated')
    return j2shim.r2r('webview/pending_labels.html', { 'labels': labels }, request=request)


@login_required
def create_screenshot(request, obj=None):
    """
    Simple form to allow registereed users to create a new screenshot entry.
    """
    auto_approve = getattr(settings, 'ADMIN_AUTO_APPROVE_SCREENSHOT', 0)
    error=""

    if request.method == 'POST':
        # Check to see if moderation settings allow for the check
        if request.user.is_staff and auto_approve == 1:
            # Automatically approved due to Moderator status
            status = 'A'
        else:
            status = 'U'

    if request.method == 'POST':
        new_screenshot = None
        l = m.Screenshot(added_by = request.user, status = status)
        form = f.CreateScreenshotForm(request.POST, request.FILES, instance = l)
        form2 = f.GenericInfoForm(request.POST)

        if form2.is_valid():
            connectval = request.POST.get("connectto")

            ct = form2.cleaned_data['content_type']
            id = form2.cleaned_data['object_id']

            # User links existing screenshot instead of creating new.
            if connectval:
                try:
                    if connectval.isdigit():
                        new_screenshot = m.Screenshot.objects.get(id=connectval)
                    else:
                        new_screenshot = m.Screenshot.objects.get(name=connectval)

                    if not new_screenshot.is_active():
                        error = "'{0}' is not active! Get an admin to approve it.".format(connectval)
                        new_screenshot = None
                    else:
                        m.ScreenshotObjectLink.objects.create(content_type=ct, object_id=id, image=new_screenshot)
                        new_screenshot.save()
                except:
                    error = "Screenshot not found!"

            if not connectval and form.is_valid():
                new_screenshot = form.save(commit=False)
                new_screenshot.save()
                form.save_m2m()

                m.ScreenshotObjectLink.objects.create(content_type=ct, object_id=id, image=new_screenshot)

                # Generate a request for the thumbnail
                new_screenshot.create_thumbnail()
                new_screenshot.save()

                # Leave this place :)

            if new_screenshot:
                return HttpResponseRedirect(new_screenshot.get_absolute_url())
    else:
        if obj:
            ct = ContentType.objects.get_for_model(obj.__class__)
            i = {'content_type': ct, 'object_id': obj.id }
        else:
            i = {}
        form = f.CreateScreenshotForm()
        form2 = f.GenericInfoForm(initial=i)

    return j2shim.r2r('webview/create_screenshot.html', \
        {'form' : form, 'form2': form2, "obj":obj, 'error':error }, \
        request=request)

@permission_required('webview.change_screenshot')
def activate_screenshots(request):
    """
    Shows the most recently added labels who have a 'U' status in their upload marker
    """
    if "screenshot" in request.GET and "status" in request.GET:
        screenshotid = int(request.GET['screenshot'])
        status = request.GET['status']
        this_screenshot = m.Screenshot.objects.get(id=screenshotid)
        url = m.Site.objects.get_current()

        if status == 'A':
            stat = "Accepted"
            this_screenshot.status = "A"
        if status == 'R':
            stat = "Rejected"
            this_screenshot.status = 'R'

        # Prepare a mail template to inform user of the status of their request
        mail_tpl = loader.get_template('webview/email/screenshot_approval.txt')
        c = Context({
                'screenshot' : this_screenshot,
                'site' : m.Site.objects.get_current(),
                'stat' : stat,
                'url' : url,
        })
        this_screenshot.save()

        # Send the email to inform the user of their request status
        if this_screenshot.added_by.get_profile().email_on_group_add and status == 'A' or status == 'R':
            this_screenshot.added_by.get_profile().send_message(
                sender = request.user,
                message = mail_tpl.render(c),
                subject = "Screenshot Request Status Changed To: %s" % stat
            )

    screenshots = m.Screenshot.objects.filter(status = "U").order_by('last_updated')
    return j2shim.r2r('webview/pending_screenshots.html', { 'screenshots': screenshots }, request=request)

@permission_required('webview.change_screenshot')
def rebuild_thumb(request, screenshot_id):
    screenshot = get_object_or_404(m.Screenshot, id=screenshot_id) #m.Screenshot.objects.get(id=screenshot_id)  #get_object_or_404(m.Screenshot, id=screenshot_id)
    screenshot.create_thumbnail()
    screenshot.save()
    return j2shim.r2r('webview/screenshot_detail.html', { 'object' : screenshot }, request)

def users_online(request):
    timefrom = datetime.datetime.now() - datetime.timedelta(minutes=5)
    userlist = m.Userprofile.objects.filter(last_activity__gt=timefrom).order_by('user__username')
    return j2shim.r2r('webview/online_users.html', {'userlist' : userlist}, request=request)

@login_required
def set_rating_autovote(request, song_id, user_rating):
    """
    Set a user's rating on a song. From 0 to 5
    """
    int_vote = int(user_rating)
    if int_vote <= 5 and int_vote > 0:
        S = m.Song.objects.get(id = song_id)
        S.set_vote(int_vote, request.user)
        #add_event(event="nowplaying")

        # Successful vote placed.
        try:
            refer = request.META['HTTP_REFERER']
            return HttpResponseRedirect(refer)
        except:
            return HttpResponseRedirect("/")

    # If the user tries any funny business, we redirect to the queue. No messing!
    return HttpResponseRedirect(reverse("dv-queue"))

@login_required
def set_rating(request, song_id):
    """
    Set a user's rating on a song. From 0 to 5
    """
    if request.method == 'POST':
        try:
            R = int(request.POST['Rating'])
        except:
             return HttpResponseRedirect(reverse('dv-song', args=[song_id]))
        if R <= 5 and R >= 1:
            S = m.Song.objects.get(id = song_id)
            S.set_vote(R, request.user)
    return HttpResponseRedirect(S.get_absolute_url())

def link_category(request, slug):
    """
    View all links associated with a specific link category slug
    """
    link_cat = get_object_or_404(m.LinkCategory, id_slug = slug)
    link_data_txt = m.Link.objects.filter(status="A").filter(link_type="T").filter(url_cat=link_cat) # See what linkage data we have
    return j2shim.r2r('webview/links_category.html', \
            {'links_txt' : link_data_txt, 'cat' : link_cat}, \
            request=request)

@login_required
def link_create(request):
    """
    User submitted links appear using this form for moderators to approve. Once sent, they are directed to
    A generic 'Thanks' page.
    """
    auto_approve = getattr(settings, 'ADMIN_AUTO_APPROVE_LINK', 0)

    if request.method == 'POST':
        # Check to see if moderation settings allow for the check
        if request.user.is_staff and auto_approve == 1:
            # Automatically approved due to Moderator status
            status = 'A'
        else:
            status = 'P'

        l = m.Link(submitted_by = request.user, status = status)
        form = f.CreateLinkForm(request.POST, request.FILES, instance = l)
        if form.is_valid():
            new_link = form.save(commit=False)
            new_link.save()
            form.save_m2m()
            return j2shim.r2r('webview/link_added.html', request=request) # Redirect to 'Thanks!' screen!
    else:
        form = f.CreateLinkForm()
    return j2shim.r2r('webview/create_link.html', { 'form' : form }, request=request)

@permission_required('webview.change_link')
def activate_links(request):
    """
    Show all currently pending links in the system. Only the l33t may access.
    """
    if "link" in request.GET and "status" in request.GET:
        linkid = int(request.GET['link'])
        status = request.GET['status']
        this_link = m.Link.objects.get(id=linkid)

        if status == 'A':
            this_link.status = "A"
            this_link.log(request.user, "Accepted link")
            this_link.approved_by = request.user
        if status == 'R':
            this_link.status = "R"
            this_link.log(request.user, "Rejected link")
            this_link.approved_by = request.user

        # Save this to the DB
        this_link.save()

    #links = Link.objects.filter(status = "P")
    links_txt = m.Link.objects.filter(status="P").filter(link_type="T")
    #links_but = Link.objects.filter(status="P").filter(link_type="U")
    #links_ban = Link.objects.filter(status="P").filter(link_type="B")
    return j2shim.r2r('webview/pending_links.html', { 'text_links' : links_txt }, request=request)

def site_links(request):
    """
    Show all active links for this site
    """
    link_cats = m.LinkCategory.objects.all() # All categories in the system
    return j2shim.r2r('webview/site-links.html', { 'link_cats' : link_cats }, request=request)

def memcached_status(request):
    try:
        import memcache
    except ImportError:
        return HttpResponseRedirect("/")

    if not (request.user.is_authenticated() and
            request.user.is_staff):
        return HttpResponseRedirect("/")

    # get first memcached URI
    match = re.match(
        "memcached://([.\w]+:\d+)", settings.CACHE_BACKEND
    )
    if not match:
        return HttpResponseRedirect("/")

    host = memcache._Host(match.group(1))
    host.connect()
    host.send_cmd("stats")

    class Stats:
        pass

    stats = Stats()

    while 1:
        line = host.readline().split(None, 2)
        if line[0] == "END":
            break
        stat, key, value = line
        try:
            # convert to native type, if possible
            value = int(value)
            if key == "uptime":
                value = datetime.timedelta(seconds=value)
            elif key == "time":
                value = datetime.datetime.fromtimestamp(value)
        except ValueError:
            pass
        setattr(stats, key, value)

    host.close_socket()

    return j2shim.r2r(
        'webview/memcached_status.html', dict(
            stats=stats,
            hit_rate=100 * stats.get_hits / stats.cmd_get,
            time=datetime.datetime.now(), # server time
        ), request=request)

class LicenseList(WebView):
    template = "licenselist.html"

    def set_context(self):
        licenses = m.SongLicense.objects.all()
        return {'licenses': licenses}

class License(WebView):
    template = "license.html"

    def set_context(self):
        id = self.kwargs.get("id")
        license = m.SongLicense.objects.get(id=id)
        return {'license': license}

class Login(MyBaseView):
    template="registration/login.html"

    MAX_FAILS_PER_HOUR = getattr(settings, "MAX_FAILED_LOGINS_PER_HOUR", 5)

    def pre_view(self):
        self.context['next'] = self.request.REQUEST.get("next", "")
        self.context['username'] = self.request.REQUEST.get("username", "")
        self.context['error'] = ""

    def check_limit(self, keys):
        for key in keys:
            if cache.get(key, 0) > self.MAX_FAILS_PER_HOUR:
                return True
        return False

    def add_to_limit(self, keys):
        for key in keys:
            if cache.get(key, None) == None:
                cache.set(key, 1, 60*60)
            else:
                cache.incr(key)

    def POST(self):
        ip = self.request.META.get("REMOTE_ADDR")

        username = self.request.POST.get('username', "")
        password = self.request.POST.get('password', "")

        key1 = hashlib.md5("loginfail" + username).hexdigest()
        key2 = hashlib.md5("loginfail" + ip).hexdigest()
        if self.check_limit((key1, key2)):
            self.context['error'] = _("Too many failed logins. Please wait an hour before trying again.")
            return False

        next = self.request.POST.get("next", False)

        if not username or not password:
            self.context['error'] = _(u"You need to supply a username and password")
            return

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return self.redirect(next or 'dv-root')
            else:
                self.context['error'] = _(u"I'm sorry, your account have been disabled.")
        else:
            self.add_to_limit((key1, key2))
            self.context['error'] = _(u"I'm sorry, the username or password seem to be wrong.")

def play_stream(request):
    streamurl = getattr(settings, "FLASH_STREAM_URL", False)
    if not streamurl:
        surl = m.RadioStream.objects.filter(streamtype="M").order_by('?')
        if surl:
            streamurl = surl[0].url
        else:
            streamurl = "No MP3 Streams!"
    return j2shim.r2r(
        'webview/radioplay.html', dict(
            streamurl=streamurl,
        ), request=request)

def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')
