from haystack.query import SearchQuerySet
from haystack.forms import ModelSearchForm
from mybaseview import MyBaseView
from webview import models as wm

import re

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.http import HttpResponse
# Create your views here.

class MMs(ModelSearchForm):
    RE = re.compile(r'(^|\s)(?P<word>\w+\*)(\s|$)', re.I)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data['q']:
            return self.no_query_found()

        q = self.cleaned_data['q']
        q = q.replace("-", " ")
        star = []
        s = self.RE.findall(q)
        if s:
            for x in s:
                w = x[1]
                q = q.replace(w, "")
                star.append(w)
        sqs = self.searchqueryset.auto_query(q)

        for w in star:
            sqs = sqs.filter(text__startswith=w)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs.models(*self.get_models())

class Ms(MMs):

    def __init__(self, *args, **kwargs):
        super(Ms, self).__init__(*args, **kwargs)
        del self.fields['models']

    def get_models(self):
        return [wm.Song]

class SearchView(MyBaseView):
    basetemplate = "search/"
    template = "search.html"
    searchtype = "All"

    def pre_view(self):
        if self.request.GET.get("songsonly"):
            u = reverse("s-song")
            u = u + "?" + self.request.META.get("QUERY_STRING")
            return HttpResponseRedirect(u)

    def GET(self):
        self.form = MMs(self.request.GET)

    def set_context(self):
        sqs = sugg = None
        if self.form.is_valid():
            q = self.form.cleaned_data['q']
            if q:
                sqs = self.form.search()
                sugg = sqs.spelling_suggestion()
                if sugg:
                    sugg = sugg.decode("utf8")
                    sugg = sugg.split(" ")[0]
                test = SearchQuerySet().filter(content=sugg).models(*self.form.get_models())
                if not test:
                    sugg = None
        return {'sqs': sqs, 'sugg': sugg, 'form': self.form, "query": q, "type": self.searchtype}

class SongSearch(SearchView):
    template = "search_songs.html"
    searchtype = "Songs"

    def pre_view(self):
        pass

    def GET(self):
        self.form = Ms(self.request.GET)
        self.form.load_all = True

class AjaxSearch(MyBaseView):
    content_type = "application/json"
    model = None

    def pre_view(self):
        self.q = self.request.GET.get("q", "")
        self.start = int(self.request.GET.get("start", "0"))
        self.num   = int(self.request.GET.get("num", "20"))
        self.context['start'] = self.start
        if not self.q:
            self.set_error("No query sent")
            return self.render()

    def set_error(self, error):
        self.context['error'] = error

    def query(self, model, keyname="results"):
        results = SearchQuerySet().auto_query(self.q).models(self.model).load_all()
        self.context['total'] = len(results)
        results = results[self.start:self.start + self.num]
        self.context['returned'] = len(results)
        results = [self.make_info(s.object) for s in results]
        if not results:
            self.set_error("No results found")
            return {}
        return {keyname: results}

    def render(self):
        return HttpResponse(simplejson.dumps(self.context), mimetype=self.content_type)


class GroupAjax(AjaxSearch):
    model = wm.Group
    def make_info(self, group):
        return {'name': group.name, 'id': group.id}

    def set_context(self):
        return self.query(wm.Group, "groups")

class ArtistAjax(AjaxSearch):
    model = wm.Artist

    def make_info(self, artist):
        groups = [{'name':x.name,'id': x.id} for x in artist.groups.all()]
        data = {'handle': artist.handle, 'id':artist.id, 'url': artist.get_absolute_url(), 'name': artist.name}
        if groups:
            data['groups'] = groups
        return data

    def set_context(self):
        return self.query(wm.Artist, "artists")

class SongAjax(AjaxSearch):
    idlist = re.compile(r'^(\d+,)+\d+$')
    model = wm.Song

    def make_artists(self, song):
        r = []
        for x in song.get_metadata().artists.all():
            r.append({'id': x.id, 'handle': x.handle, 'url': x.get_absolute_url() })
        return r

    def make_info(self, song):
        return {"title": song.title, "artists": self.make_artists(song), "id": song.id, "url": song.get_absolute_url(), "songlength": song.get_songlength()}

    def get_songs_from_list(self, songs):
        return [self.make_info(wm.Song.objects.get(id=s)) for s in songs]

    def set_context(self):
        songs = []
        count = 0

        query = self.q

        if query.isdigit():
            try:
                songs = [self.make_info(wm.Song.objects.get(id=query))]
                count = 1
            except:
                self.set_error("No song match that ID")

        elif self.idlist.match(query):
            try:
                songs = self.get_songs_from_list(query.split(","))
                count = len(songs)
            except:
                self.set_error("Some song ID's were not found!")

        else:
            songs = self.query(wm.Song, "songs")
            return songs

        return {
            'songs': songs,
            'count': count,
        }


class SongAjax2(SongAjax):

    def set_context(self):
        return self.query(wm.Song, "songs")
