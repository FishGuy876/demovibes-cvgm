## Imports

from django.conf.urls.defaults import patterns
from demovibes.webview.models import SongType, RadioStream, Compilation, Group
from demovibes.webview.xml_views import UserFavorites, UserInfo, ArtistInfo, SongInfo
from django.views.generic.list_detail import object_detail, object_list
from tagging.models import Tag

## Dicts

tag_dict = {
    'queryset': Tag.objects.all(),
    'mimetype': "application/xml",
    'template_name': 'webview/xml/tags.xml',
}

songtype_dict = {
    'queryset': SongType.objects.all(),
    'mimetype': "application/xml",
    'template_name': 'webview/xml/songtypes.xml',
}

stream_dict = {
    'queryset' : RadioStream.objects.all(),
    'mimetype': "application/xml",
    'template_name': 'webview/xml/streams.xml',
}

compilation_dict = {
    'queryset': Compilation.objects.all(),
    'mimetype': "application/xml",
    'template_name': 'webview/xml/compilation.xml',
}

group_dict = {
    'queryset': Group.objects.all(),
    'mimetype': "application/xml",
    'template_name': 'webview/xml/group.xml',
}

## Methods

def cached_object_list(*args, **kwargs):
    return object_list(*args, **kwargs)

def cached_object_detail(*args, **kwargs):
    return object_detail(*args, **kwargs)

## URL patterns

urlpatterns = patterns (
    '',
    (r'^queue/$',                                   'demovibes.webview.xml_views.queue'),
    (r'^oneliner/$',                                'demovibes.webview.xml_views.oneliner'),
    (r'^online/$',                                  'demovibes.webview.xml_views.online'),
    (r'^song/(?P<songid>\d+)/$',                    SongInfo()),
    (r'^compilation/(?P<object_id>\d+)/$',          cached_object_detail,   compilation_dict),
    (r'^group/(?P<object_id>\d+)/$',                cached_object_detail,   group_dict),
    (r'^artist/(?P<id>\d+)/$',                      ArtistInfo()),
    (r'^artist/handle/(?P<handle>.{1,64})/$',       ArtistInfo()),
    (r'^streams/$',                                 cached_object_list,     stream_dict),
    (r'^tags/$',                                    cached_object_list,     tag_dict),
    (r'^songtypes/$',                               cached_object_list,     songtype_dict),
    (r'^user/(?P<username>\w+)/$',                  UserInfo()),
    (r'^user/(?P<username>\w+)/favorites/$',        UserFavorites()),
)

## Local words for flyspell
#  LocalWords:  xml queryset oneliner online username songtypes
#  LocalWords:  songid mimetype
