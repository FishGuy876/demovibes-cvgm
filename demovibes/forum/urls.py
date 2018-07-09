"""
URLConf for Django-Forum.

django-forum assumes that the forum application is living under
/forum/.

Usage in your base urls.py:
    (r'^forum/', include('forum.urls')),

"""

from django.conf.urls.defaults import *
from forum.models import Forum, Post
from forum.feeds import RssForumFeed, AtomForumFeed
import djangojinja2  

forum_dict = {
    'queryset' : Forum.objects.filter(parent__isnull=True),
    'template_loader': djangojinja2._jinja_env,
}

feed_dict = {
    'rss' : RssForumFeed,
    'atom': AtomForumFeed
}

urlpatterns = patterns('',
    url(r'^$', 'forum.views.forum_list', name='forum_index'),
    
    url(r'^(?P<url>(rss|atom).*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feed_dict}),

    url(r'^thread/(?P<thread>[0-9]+)/$', 'forum.views.thread', name='forum_view_thread'),
    url(r'^edit/(?P<post_id>\d+)/$', 'forum.views.edit'),

    url(r'^subscriptions/$', 'forum.views.updatesubs', name='forum_subscriptions'),

    url(r'^(?P<slug>[-\w]+)/$', 'forum.views.forum', name='forum_thread_list'),

    url(r'^([-\w/]+/)(?P<slug>[-\w]+)/$', 'forum.views.forum', name='forum_subforum_thread_list'),
)
