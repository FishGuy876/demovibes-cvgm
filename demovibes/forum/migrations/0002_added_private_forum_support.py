
from south.db import db
from django.db import models
from demovibes.forum.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Forum.is_private'
        db.add_column('forum_forum', 'is_private', models.BooleanField(_("Staff Only?"), null=True, blank=True))
        
        # Changing field 'Forum.posts'
        db.alter_column('forum_forum', 'posts', models.IntegerField(_("Posts"), default=0, editable=False))
        
        # Changing field 'Forum.threads'
        db.alter_column('forum_forum', 'threads', models.IntegerField(_("Threads"), default=0, editable=False))
        
        # Changing field 'Thread.sticky'
        db.alter_column('forum_thread', 'sticky', models.BooleanField(_("Sticky?"), default=False, blank=True))
        
        # Changing field 'Thread.closed'
        db.alter_column('forum_thread', 'closed', models.BooleanField(_("Closed?"), default=False, blank=True))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Forum.is_private'
        db.delete_column('forum_forum', 'is_private')
        
        # Changing field 'Forum.posts'
        db.alter_column('forum_forum', 'posts', models.IntegerField(_("Posts"), default=0))
        
        # Changing field 'Forum.threads'
        db.alter_column('forum_forum', 'threads', models.IntegerField(_("Threads"), default=0))
        
        # Changing field 'Thread.sticky'
        db.alter_column('forum_thread', 'sticky', models.BooleanField(_("Sticky?"), default=False, null=True, blank=True))
        
        # Changing field 'Thread.closed'
        db.alter_column('forum_thread', 'closed', models.BooleanField(_("Closed?"), default=False, null=True, blank=True))
        
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'forum.forum': {
            'Meta': {'ordering': "['title',]"},
            'description': ('models.TextField', ['_("Description")'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_private': ('models.BooleanField', ['_("Staff Only?")'], {'null': 'True', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["'self'"], {'related_name': "'child'", 'null': 'True', 'blank': 'True'}),
            'posts': ('models.IntegerField', ['_("Posts")'], {'default': '0', 'editable': 'False'}),
            'slug': ('models.SlugField', ['_("Slug")'], {}),
            'threads': ('models.IntegerField', ['_("Threads")'], {'default': '0', 'editable': 'False'}),
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
            'closed': ('models.BooleanField', ['_("Closed?")'], {'default': 'False', 'blank': 'True'}),
            'forum': ('models.ForeignKey', ['Forum'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'latest_post_time': ('models.DateTimeField', ['_("Latest Post Time")'], {'null': 'True', 'blank': 'True'}),
            'posts': ('models.IntegerField', ['_("Posts")'], {'default': '0'}),
            'sticky': ('models.BooleanField', ['_("Sticky?")'], {'default': 'False', 'blank': 'True'}),
            'title': ('models.CharField', ['_("Title")'], {'max_length': '100'}),
            'views': ('models.IntegerField', ['_("Views")'], {'default': '0'})
        }
    }
    
    complete_apps = ['forum']
