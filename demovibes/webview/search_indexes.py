from haystack.indexes import *
from haystack import site
from django.conf import settings
import webview.models as M

class ArtistIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    render = CharField(indexed=False, use_template=True)
    country = CharField(model_attr="home_country")

    def get_queryset(self):
        return M.Artist.objects.all()

    def get_updated_field(self):
        return "last_updated"

class SongIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    render = CharField(indexed=False, use_template=True)

    # Need haystack 1.2 for this
    #title = CharField(model_attr='title', boost=5.0)

    def get_queryset(self):
        return M.Song.objects.all()

    def get_updated_field(self):
        return "last_changed"

    # Need haystack 1.2 for this
    def prepare(self, obj):
        data = super(SongIndex, self).prepare(obj)
        # Boost is not working on whoosh
        if obj.status == "A" and settings.HAYSTACK_SEARCH_ENGINE != "whoosh":
            data['boost'] = 5.0
        return data

class GroupIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    render = CharField(indexed=False, use_template=True)

    def get_queryset(self):
        return M.Group.objects.all()

    def get_updated_field(self):
        return "last_updated"

class UserIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    render = CharField(indexed=False, use_template=True)

    def get_queryset(self):
        return M.Userprofile.objects.filter(visible_to = "A")

    def get_updated_field(self):
        return "last_changed"

site.register(M.Group, GroupIndex)
site.register(M.Song, SongIndex)
site.register(M.Artist, ArtistIndex)
site.register(M.Userprofile, UserIndex)
