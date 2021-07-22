from django.conf.urls.defaults import *
from demovibes.webview.models import *
from django.conf import settings
from demovibes.webview import views
import djangojinja2

oneliner_dict = {
    'queryset': Oneliner.objects.all(),
    'template_loader': djangojinja2._jinja_env,
}


"""
Access any artist object.
"""
artist_a_dict = {
    'queryset': Artist.objects.all(),
    'template_loader': djangojinja2._jinja_env,
}

"""
Access any group object.
"""
group_a_dict = {
    'queryset': Group.objects.all(),
    'template_loader': djangojinja2._jinja_env,
}

"""
Queries pending labels, needs to be all or pending wont show
"""
labels_a_dict = {
    'queryset': Label.objects.all(),
    'template_loader': djangojinja2._jinja_env,
}

news_dict = {
    'queryset': News.objects.all(),
    'template_loader': djangojinja2._jinja_env,
}

streams_dict_txt = {
    'queryset': RadioStream.objects.filter(active=True, streamtype = 'M'),
    'template_loader': djangojinja2._jinja_env,
}
streams_dict_m3u = {
    'queryset': RadioStream.objects.filter(active=True, streamtype = 'M'),
    'template_loader': djangojinja2._jinja_env,
    'template_name': "webview/streamlist_m3u.html",
}

streams_dict = {
    'queryset': RadioStream.objects.filter(active=True).order_by('name'),
    'template_name' : "webview/streams.html",
    'template_loader': djangojinja2._jinja_env,
}

"""
Retreive all FAQ Questions marked as 'Active'
"""
faq_dict = {
    'queryset': Faq.objects.filter(active=True),
    'template_loader': djangojinja2._jinja_env,
}

platforms = {
    'queryset' : SongPlatform.objects.all(),
    'template_loader': djangojinja2._jinja_env,
    #'paginate_by': 500,
}

sources = {
    'queryset' : SongType.objects.all(),
    'template_loader': djangojinja2._jinja_env,
    #'paginate_by': 500,
}

urlpatterns = patterns('',
    # First, some generic 'site' areas commonly found on any site
    url(r'^about/$',                              'demovibes.webview.views.site_about', name = "dv-about"),
    url(r'^login/$',                               views.Login(), name = "dv-login"),
    url(r'^licenses/$',                            views.LicenseList(), name = "dv-licenses"),
    url(r'^license/(?P<id>\d+)/$',                 views.License(), name = "dv-license"),
    url(r'^smileys/$',                              views.ListSmileys(), name = "dv-smileys"),

    url(r'^inbox/$',                               'demovibes.webview.views.inbox', name = "dv-inbox"),
    url(r'^inbox/(?P<pm_id>\d+)/$',                'demovibes.webview.views.read_pm', name = "dv-read_pm"),
    url(r'^inbox/send/$',                          'demovibes.webview.views.send_pm', name = "dv-send_pm"),

    url(r'^play/$',                                'demovibes.webview.views.play_stream', name = "dv-play_stream"),

    #url(r'^play/$',                                'django.views.generic.simple.direct_to_template', \
    #            { 'template':'webview/radioplay.html'}, name = "dv-play_stream"),
    url(r'^$',                                     'django.views.generic.list_detail.object_list',     news_dict, name = "dv-root"),
    url(r'^streams/streams.txt$',                  'django.views.generic.list_detail.object_list',     streams_dict_txt, name = "dv-streams.txt"),
    url(r'^streams/streams.m3u$',                  'django.views.generic.list_detail.object_list',     streams_dict_m3u, name = "dv-streams.m3u"),
    url(r'^streams/$',                             'django.views.generic.list_detail.object_list',     streams_dict, name = "dv-streams"),
    url(r'^oneliner/$',                            'django.views.generic.list_detail.object_list', \
                dict(oneliner_dict, paginate_by=settings.PAGINATE), name = "dv-oneliner"),
    url(r'^oneliner/mute/$',                       views.MuteOneliner(), name = "dv-muteoneliner"),
    url(r'^oneliner/lookie/$',                       views.OnelinerHistorySearch(), name = "dv-onelinerhsearch"),
    #url(r'^search/$',                              'demovibes.webview.views.search', name = "dv-search"),
    url(r'^recent/$',                              'demovibes.webview.views.show_approvals', name = "dv-recent"),
    url(r'^platform/(?P<object_id>\d+)/$',         'django.views.generic.list_detail.object_detail', platforms, name = "dv-platform"),
    url(r'^platforms/$',                           'django.views.generic.list_detail.object_list', platforms, name = "dv-platforms"),

    url(r'^sources/$',                           'django.views.generic.list_detail.object_list', sources, name = "dv-sources"),
    url(r'^source/(?P<object_id>\d+)/$',         'django.views.generic.list_detail.object_detail', sources, name = "dv-source"),

    url(r'^chat/$',             'demovibes.webview.views.chat', name = "dv-chat"),

    # Screenshot stuff
    url(r'^screenshots/$',                       views.ListScreenshots(), name = "dv-screenshots"),
    url(r'^screenshots/(?P<letter>.)/$',         views.ListScreenshots(), name = "dv-screenshots_letter"),
    url(r'^screenshot/(?P<screenshot_id>\d+)/$', 'demovibes.webview.views.list_screenshot',   name = "dv-screenshot"),
    url(r'^screenshot/(?P<screenshot_id>\d+)/rethumb/$', 'demovibes.webview.views.rebuild_thumb',   name = "dv-screenshot-rethumb"),
    url(r'^screenshot/create/$',                    'demovibes.webview.views.create_screenshot', name = "dv-createscreenshot"),
    url(r'^new_screenshots/$',                      'demovibes.webview.views.activate_screenshots', name = "dv-newscreenshots"),

    #Song views
    url(r'^newshit/$',                          'demovibes.webview.views.new_songinfo_list', name="dv-new-info"),
    url(r'^songs/$',                               views.ListSongs(), name = "dv-songs"),
    url(r'^songs/(?P<letter>.)/$',                 views.ListSongs(), name = "dv-songs_letter"),
    url(r'^songs/year/(?P<year_id>\d+)/$',             'demovibes.webview.views.list_year',   name = "dv-year"),
    url(r'^song/(?P<song_id>\d+)/$',             'demovibes.webview.views.list_song',   name = "dv-song"),
    url(r'^song/(?P<song_id>\d+)/addlink/$',             'demovibes.webview.views.add_songlinks',   name = "dv-song-addlink"),
    url(r'^song/(?P<song_id>\d+)/edit/$',             'demovibes.webview.views.edit_songinfo',   name = "dv-song-edit"),
    url(r'^song/(?P<song_id>\d+)/infolist/$',             'demovibes.webview.views.list_songinfo_for_song',   name = "dv-song-infolist"),
    url(r'^song/(?P<song_id>\d+)/comments/$',      views.songComments(), name = "dv-song_comment"),
    url(r'^song/(?P<song_id>\d+)/votes/$',         views.songVotes(), name = "dv-song_votes"),
    url(r'^song/(?P<song_id>\d+)/queue_history/$', views.songHistory(), name = "dv-song_history"),
    
    url(r'^song/queue/$',                               views.QueueSong(), name = "dv-queue-song"),
    url(r'^song/(?P<song_id>\d+)/screenshot/$',    views.SongAddScreenshot(), name = "dv-add_screenshot"),
    url(r'^song/(?P<song_id>\d+)/play/$',          views.PlaySong(), name = "dv-play_song"),
    url(r'^song/vote/$',          views.VoteSong(), name = "dv-formvote"),

    url(r'^metainfo/(?P<songinfo_id>\d+)/$',             'demovibes.webview.views.view_songinfo',   name = "dv-songinfo-view"),

    url(r'^groups/$',                             views.ListGroups(), name = "dv-groups"),
    url(r'^groups/(?P<letter>.)/$',               views.ListGroups(), name = "dv-groups_letter"),
    url(r'^group/(?P<object_id>\d+)/$',            'django.views.generic.list_detail.object_detail',       group_a_dict, name = "dv-group"),

    url(r'^statistics/$',                                   views.RadioStatus(), name = "dv-stats-index"),
    url(r'^statistics/overview/radio/$',                    views.RadioOverview(), name = "dv-radio-overview"),
    url(r'^statistics/overview/users/$',                    views.UsersOverview(), name = "dv-users-overview"),
    url(r'^statistics/helpus/artisthelp/$',                 views.HelpusWithArtists(), name = "dv-helpus-artist"),
    url(r'^statistics/helpus/artisthelp/(?P<letter>.)/$',   views.HelpusWithArtists(), name = "dv-helpus-artist_letter"),
    url(r'^statistics/helpus/songhelp/$',                   views.HelpusWithSongs(), name = "dv-helpus-song"),
    url(r'^statistics/helpus/songhelp/(?P<letter>.)/$',     views.HelpusWithSongs(), name = "dv-helpus-song_letter"),
    url(r'^statistics/helpus/comphelp/$',                   views.HelpusWithComps(), name = "dv-helpus-comp"),
    url(r'^statistics/helpus/comphelp/(?P<letter>.)/$',     views.HelpusWithComps(), name = "dv-helpus-comp_letter"),
    url(r'^statistics/helpus/sshelp/$',                     views.HelpusWithScreenshots(), name = "dv-helpus-screenshot"),
    url(r'^statistics/helpus/sshelp/(?P<letter>.)/$',       views.HelpusWithScreenshots(), name = "dv-helpus-screenshot_letter"),
    url(r'^statistics/(?P<stattype>\w+)/$',                 views.RadioStatus(), name = "dv-stats"),

    # Updated Information, such as groups, labels etc.
    url(r'^updates/$',                  'demovibes.webview.views.showRecentChanges', name = "dv-updates"),

    url(r'^artists/$',                             views.ListArtists(), name = "dv-artists"),
    url(r'^artists/(?P<letter>.)/$',               views.ListArtists(), name = "dv-artists_letter"),
    url(r'^artist/(?P<object_id>\d+)/$',           'django.views.generic.list_detail.object_detail',       artist_a_dict, name = "dv-artist"),
    url(r'^artist/(?P<artist_id>\d+)/upload/$',    'demovibes.webview.views.upload_song', name = "dv-upload"),

    # Add support for displaying all compilations
    url(r'^compilations/$',                                     views.ListComilations(), name = "dv-compilations"),
    url(r'^compilations/new/$',                                 views.AddCompilation(), name = "dv-newcomp"),
    url(r'^compilations/(?P<letter>.)/$',                       views.ListComilations(), name = "dv-compilations_letter"),
    url(r'^compilation/(?P<compilation_id>\d+)/screenshot/$',   views.CompilationAddScreenshot(), name = "dv-add_comp_screenshot"),

    url(r'^user/$',                                views.MyProfile(), name = "dv-my_profile"),
    url(r'^online/$',                              'demovibes.webview.views.users_online', name = "dv-users_online"),
    url(r'^user/(?P<user>\w+)/$',                  views.ViewProfile(), name = "dv-profile"),
    url(r'^user/(?P<user>\w+)/favorites/$',        views.ViewUserFavs(), name = "dv-user-favs"),
    url(r'^queue/$',                               views.ListQueue(), name = "dv-queue"),
    url(r'^comment/add/(?P<song_id>\d+)/$',        views.addComment(), name = "dv-addcomment"),

    url(r'^tags/$',                                views.TagCloud(), name = "dv-tagcloud"),
    url(r'^tags/(?P<tag>[^/]+)/$',                 views.TagDetail(), name = "dv-tagdetail"),
    url(r'^song/(?P<song_id>\d+)/tags/$',          views.TagEdit(), name = "dv-songtags"),

    url(r'^themes/$',                                views.ThemeList(), name = "dv-themelist"),
    url(r'^theme/(?P<theme_id>\d+)/$',               views.ThemeInfo(), name = "dv-themeinfo"),
    url(r'^theme/(?P<theme_id>\d+)/add_image/$',     views.ThemeAddImage(), name = "dv-themeaddimage"),
    url(r'^theme/(?P<theme_id>\d+)/edit/$',         views.ThemeEdit(), name = "dv-themeedit"),

    url(r'^favorites/change/$',                     views.ChangeFavorite(), name = "dv-change_fav"),
    url(r'^favorites/$',                           'demovibes.webview.views.list_favorites', name = "dv-favorites"),
    url(r'^uploaded_songs/$',                      'demovibes.webview.views.activate_upload', name = "dv-uploads"),
    url(r'^upload_progress/$',                      'demovibes.webview.views.upload_progress', name = "dv-upload-progress"),
    url(r'^oneliner/submit/$',                     'demovibes.webview.views.oneliner_submit', name = "dv-oneliner_submit"),
    (r'^ajax/',                                    include('demovibes.webview.ajax_urls')),
    (r'^xml/',                                     include('demovibes.webview.xml_urls')),

    # Compilation Views
    url(r'^compilation/(?P<comp_id>\d+)/$',             'demovibes.webview.views.view_compilation',       name = "dv-compilation"),
    url(r'^compilation/(?P<comp_id>\d+)/edit/$',         views.EditCompilation(),       name = "dv-compilation-edit"),

    # Creation URL's for users to make new stuff
    url(r'^artist/create/$',                    'demovibes.webview.views.create_artist', name = "dv-createartist"),
    url(r'^new_artists/$',                      'demovibes.webview.views.activate_artists', name = "dv-newartists"),
    url(r'^group/create/$',                     'demovibes.webview.views.create_group', name = "dv-creategroup"),
    url(r'^new_groups/$',                       'demovibes.webview.views.activate_groups', name = "dv-newgroups"),
    url(r'^new_compilations/$',                 'demovibes.webview.views.activate_compilations', name = "dv-newcompilations"),

    # Production label URL's (Labels/Producers Specific)
    url(r'^labels/$',                             views.ListLabels(), name = "dv-labels"),
    url(r'^label/(?P<object_id>\d+)/$',            'django.views.generic.list_detail.object_detail',       labels_a_dict, name = "dv-label"),
    url(r'^labels/(?P<letter>.)/$',               views.ListLabels(), name = "dv-labels_letter"),
    url(r'^label/create/$',                    'demovibes.webview.views.create_label', name = "dv-createlabel"),
    url(r'^new_labels/$',                      'demovibes.webview.views.activate_labels', name = "dv-newlabels"),

    # Link Management
    url(r'^links/(?P<slug>[-\w]+)/$',          'demovibes.webview.views.link_category', name = "dv-linkcategory"),
    url(r'^link/create/$',                    'demovibes.webview.views.link_create', name = "dv-createlink"),
    url(r'^link/pending/$',                   'demovibes.webview.views.activate_links', name = "dv-newlinks"),
    url(r'^links/$',                           'demovibes.webview.views.site_links', name = "dv-links"), # View existing Links

    # FAQ System
    url(r'^faq/$',                                'django.views.generic.list_detail.object_list', faq_dict, name = "dv-faq"), # Generic FAQ System (All active Questions)
    url(r'^faq/(?P<object_id>\d+)/$',           'django.views.generic.list_detail.object_detail', faq_dict, name = "dv-faqitem"),

    # Statistics & Cache stuff
    url(r'^status/cache/$',                    'demovibes.webview.views.memcached_status', name = "dv-memcached"), # Show memcached status
)
