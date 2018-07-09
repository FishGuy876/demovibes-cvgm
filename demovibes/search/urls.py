from django.conf.urls.defaults import *
from demovibes.search import views

urlpatterns = patterns('',
    url(r'^$', views.SearchView(), name="s-all"),
    url(r'^song/$', views.SongSearch(), name="s-song"),
    url(r'^ajax/song/$', views.SongAjax(), name="s-song-ajax"),
    url(r'^ajax/song2/$', views.SongAjax2(), name="s-song-ajax2"),
    url(r'^ajax/artist/$', views.ArtistAjax(), name="s-artist-ajax"),
)
