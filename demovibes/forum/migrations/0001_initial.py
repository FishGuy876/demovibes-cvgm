
from south.db import db
from django.db import models
from demovibes.forum.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Forum'
        db.create_table('forum_forum', (
            ('description', models.TextField(_("Description"))),
            ('parent', models.ForeignKey(orm.Forum, related_name='child', null=True, blank=True)),
            ('title', models.CharField(_("Title"), max_length=100)),
            ('posts', models.IntegerField(_("Posts"), default=0)),
            ('id', models.AutoField(primary_key=True)),
            ('threads', models.IntegerField(_("Threads"), default=0)),
            ('slug', models.SlugField(_("Slug"))),
        ))
        db.send_create_signal('forum', ['Forum'])
        
        # Adding model 'Post'
        db.create_table('forum_post', (
            ('body', models.TextField(_("Body"))),
            ('edited', models.DateTimeField(null=True, blank=True)),
            ('thread', models.ForeignKey(orm.Thread)),
            ('author', models.ForeignKey(orm['auth.User'], related_name='forum_post_set')),
            ('time', models.DateTimeField(_("Time"), null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('forum', ['Post'])
        
        # Adding model 'Subscription'
        db.create_table('forum_subscription', (
            ('id', models.AutoField(primary_key=True)),
            ('thread', models.ForeignKey(orm.Thread)),
            ('author', models.ForeignKey(orm['auth.User'])),
        ))
        db.send_create_signal('forum', ['Subscription'])
        
        # Adding model 'Thread'
        db.create_table('forum_thread', (
            ('latest_post_time', models.DateTimeField(_("Latest Post Time"), null=True, blank=True)),
            ('forum', models.ForeignKey(orm.Forum)),
            ('title', models.CharField(_("Title"), max_length=100)),
            ('views', models.IntegerField(_("Views"), default=0)),
            ('posts', models.IntegerField(_("Posts"), default=0)),
            ('sticky', models.BooleanField(_("Sticky?"), default=False, null=True, blank=True)),
            ('closed', models.BooleanField(_("Closed?"), default=False, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('forum', ['Thread'])
        
        # Creating unique_together for [author, thread] on Subscription.
        db.create_unique('forum_subscription', ['author_id', 'thread_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Forum'
        db.delete_table('forum_forum')
        
        # Deleting model 'Post'
        db.delete_table('forum_post')
        
        # Deleting model 'Subscription'
        db.delete_table('forum_subscription')
        
        # Deleting model 'Thread'
        db.delete_table('forum_thread')
        
        # Deleting unique_together for [author, thread] on Subscription.
        db.delete_unique('forum_subscription', ['author_id', 'thread_id'])
        
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'forum.forum': {
            'Meta': {'ordering': "['title',]"},
            'description': ('models.TextField', ['_("Description")'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'parent': ('models.ForeignKey', ["'self'"], {'related_name': "'child'", 'null': 'True', 'blank': 'True'}),
            'posts': ('models.IntegerField', ['_("Posts")'], {'default': '0'}),
            'slug': ('models.SlugField', ['_("Slug")'], {}),
            'threads': ('models.IntegerField', ['_("Threads")'], {'default': '0'}),
            'title': ('models.CharField', ['_("Title")'], {'max_length': '100'})
        },
        'forum.post': {
            'Meta': {'ordering': "('-time',)"},
            'author': ('models.ForeignKey', ['User'], {'related_name': "'forum_post_set'"}),
            'body': ('models.TextField', ['_("Body")'], {}),
            'edited': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'thread': ('models.ForeignKey', ['Thread'], {}),
            'time': ('models.DateTimeField', ['_("Time")'], {'null': 'True', 'blank': 'True'})
        },
        'forum.subscription': {
            'Meta': {'unique_together': '(("author","thread"),)'},
            'author': ('models.ForeignKey', ['User'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'thread': ('models.ForeignKey', ['Thread'], {})
        },
        'forum.thread': {
            'Meta': {'ordering': "('-sticky','-latest_post_time')"},
            'closed': ('models.BooleanField', ['_("Closed?")'], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'forum': ('models.ForeignKey', ['Forum'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'latest_post_time': ('models.DateTimeField', ['_("Latest Post Time")'], {'null': 'True', 'blank': 'True'}),
            'posts': ('models.IntegerField', ['_("Posts")'], {'default': '0'}),
            'sticky': ('models.BooleanField', ['_("Sticky?")'], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'title': ('models.CharField', ['_("Title")'], {'max_length': '100'}),
            'views': ('models.IntegerField', ['_("Views")'], {'default': '0'})
        }
    }
    
    complete_apps = ['forum']
