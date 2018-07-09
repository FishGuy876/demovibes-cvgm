
from south.db import db
from django.db import models
from demovibes.webview.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Favorite'
        db.create_table('webview_favorite', (
            ('comment', models.TextField()),
            ('user', models.ForeignKey(orm['auth.User'])),
            ('added', models.DateTimeField(auto_now_add=True)),
            ('id', models.AutoField(primary_key=True)),
            ('song', models.ForeignKey(orm.Song)),
        ))
        db.send_create_signal('webview', ['Favorite'])
        
        # Adding model 'News'
        db.create_table('webview_news', (
            ('status', models.CharField(max_length=1)),
            ('added', models.DateTimeField(auto_now_add=True)),
            ('title', models.CharField(max_length=100)),
            ('text', models.TextField()),
            ('id', models.AutoField(primary_key=True)),
            ('icon', models.URLField(blank=True)),
        ))
        db.send_create_signal('webview', ['News'])
        
        # Adding model 'SongComment'
        db.create_table('webview_songcomment', (
            ('comment', models.TextField()),
            ('user', models.ForeignKey(orm['auth.User'])),
            ('added', models.DateTimeField(auto_now_add=True)),
            ('id', models.AutoField(primary_key=True)),
            ('song', models.ForeignKey(orm.Song)),
        ))
        db.send_create_signal('webview', ['SongComment'])
        
        # Adding model 'SongPlatform'
        db.create_table('webview_songplatform', (
            ('description', models.TextField()),
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(unique=True, max_length=64)),
        ))
        db.send_create_signal('webview', ['SongPlatform'])
        
        # Adding model 'RadioStream'
        db.create_table('webview_radiostream', (
            ('description', models.TextField()),
            ('url', models.CharField(max_length=120)),
            ('streamtype', models.CharField(max_length=1)),
            ('country_code', models.CharField(max_length=10)),
            ('active', models.BooleanField(default=True)),
            ('bitrate', models.IntegerField()),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=120)),
        ))
        db.send_create_signal('webview', ['RadioStream'])
        
        # Adding model 'Group'
        db.create_table('webview_group', (
            ('info', models.TextField(blank=True)),
            ('startswith', models.CharField(max_length=1, editable=False, db_index=True)),
            ('pouetid', models.IntegerField(null=True, blank=True)),
            ('name', models.CharField(unique=True, max_length=30, db_index=True)),
            ('webpage', models.URLField(blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('webview', ['Group'])
        
        # Adding model 'AjaxEvent'
        db.create_table('webview_ajaxevent', (
            ('user', models.ForeignKey(orm['auth.User'], default=None, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('event', models.CharField(max_length=100)),
        ))
        db.send_create_signal('webview', ['AjaxEvent'])
        
        # Adding model 'SongVote'
        db.create_table('webview_songvote', (
            ('vote', models.IntegerField()),
            ('user', models.ForeignKey(orm['auth.User'])),
            ('added', models.DateTimeField(auto_now_add=True)),
            ('id', models.AutoField(primary_key=True)),
            ('song', models.ForeignKey(orm.Song)),
        ))
        db.send_create_signal('webview', ['SongVote'])
        
        # Adding model 'PrivateMessage'
        db.create_table('webview_privatemessage', (
            ('sender', models.ForeignKey(orm['auth.User'], related_name="sent_messages")),
            ('to', models.ForeignKey(orm['auth.User'])),
            ('reply_to', models.ForeignKey(orm.PrivateMessage, default=None, null=True, blank=True)),
            ('message', models.TextField()),
            ('unread', models.BooleanField(default=True)),
            ('id', models.AutoField(primary_key=True)),
            ('sent', models.DateTimeField(auto_now_add=True)),
            ('subject', models.CharField(max_length=60)),
        ))
        db.send_create_signal('webview', ['PrivateMessage'])
        
        # Adding model 'Oneliner'
        db.create_table('webview_oneliner', (
            ('message', models.CharField(max_length=128)),
            ('added', models.DateTimeField(auto_now_add=True)),
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'])),
        ))
        db.send_create_signal('webview', ['Oneliner'])
        
        # Adding model 'Artist'
        db.create_table('webview_artist', (
            ('info', models.TextField(blank=True)),
            ('startswith', models.CharField(max_length=1, editable=False, db_index=True)),
            ('handle', models.CharField(unique=True, max_length=64, db_index=True)),
            ('name', models.CharField(max_length=64, blank=True)),
            ('webpage', models.URLField(blank=True)),
            ('dob', models.DateField(null=True, blank=True)),
            ('alias_of', models.ForeignKey(orm.Artist, related_name='aliases', null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('webview', ['Artist'])
        
        # Adding model 'Queue'
        db.create_table('webview_queue', (
            ('requested', models.DateTimeField(auto_now_add=True, db_index=True)),
            ('played', models.BooleanField()),
            ('song', models.ForeignKey(orm.Song)),
            ('requested_by', models.ForeignKey(orm['auth.User'])),
            ('time_played', models.DateTimeField(db_index=True, null=True, blank=True)),
            ('playtime', models.DateTimeField(db_index=True, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('priority', models.BooleanField(default=False, db_index=True)),
        ))
        db.send_create_signal('webview', ['Queue'])
        
        # Adding model 'SongType'
        db.create_table('webview_songtype', (
            ('description', models.TextField()),
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(unique=True, max_length=64)),
        ))
        db.send_create_signal('webview', ['SongType'])
        
        # Adding model 'Logo'
        db.create_table('webview_logo', (
            ('active', models.BooleanField(default=True)),
            ('description', models.TextField(blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('file', models.FileField(upload_to='media/logos')),
            ('creator', models.CharField(max_length=60)),
        ))
        db.send_create_signal('webview', ['Logo'])
        
        # Adding model 'UploadTicket'
        db.create_table('webview_uploadticket', (
            ('added', models.DateTimeField(auto_now_add=True)),
            ('tempfile', models.CharField(default="", max_length=100, blank=True)),
            ('filename', models.CharField(default="", max_length=100, blank=True)),
            ('user', models.ForeignKey(orm['auth.User'])),
            ('ticket', models.CharField(max_length=20)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('webview', ['UploadTicket'])
        
        # Adding model 'Song'
        db.create_table('webview_song', (
            ('info', models.TextField(blank=True)),
            ('startswith', models.CharField(max_length=1, editable=False, db_index=True)),
            ('pouetid', models.IntegerField(null=True, blank=True)),
            ('rating', models.FloatField(null=True, blank=True)),
            ('uploader', models.ForeignKey(orm['auth.User'], null=True, blank=True)),
            ('title', models.CharField(max_length=64, db_index=True)),
            ('rating_total', models.IntegerField(default=0)),
            ('times_played', models.IntegerField(default=0, null=True)),
            ('rating_votes', models.IntegerField(default=0)),
            ('platform', models.ForeignKey(orm.SongPlatform, null=True, blank=True)),
            ('added', models.DateTimeField(auto_now_add=True)),
            ('status', models.CharField(default='A', max_length=1)),
            ('bitrate', models.IntegerField(null=True, blank=True)),
            ('file', models.FileField(upload_to='media/music')),
            ('song_length', models.IntegerField(null=True, editable=False, blank=True)),
            ('samplerate', models.IntegerField(null=True, blank=True)),
            ('type', models.ForeignKey(orm.SongType, null=True, verbose_name='Source', blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('webview', ['Song'])
        
        # Adding model 'Userprofile'
        db.create_table('webview_userprofile', (
            ('info', models.TextField(blank=True)),
            ('group', models.ForeignKey(orm.Group, null=True, blank=True)),
            ('last_active', models.DateTimeField(null=True, blank=True)),
            ('web_page', models.URLField(blank=True)),
            ('country', models.CharField(max_length=10, blank=True)),
            ('token', models.CharField(max_length=32, blank=True)),
            ('user', models.ForeignKey(orm['auth.User'], unique=True)),
            ('id', models.AutoField(primary_key=True)),
            ('avatar', models.ImageField(null=True, upload_to='media/avatars', blank=True)),
        ))
        db.send_create_signal('webview', ['Userprofile'])
        
        # Adding model 'SongDownload'
        db.create_table('webview_songdownload', (
            ('title', models.CharField(max_length=64)),
            ('added', models.DateTimeField(auto_now_add=True)),
            ('id', models.AutoField(primary_key=True)),
            ('download_url', models.CharField(max_length=200, unique=True)),
            ('song', models.ForeignKey(orm.Song)),
        ))
        db.send_create_signal('webview', ['SongDownload'])
        
        # Adding ManyToManyField 'Song.artists'
        db.create_table('webview_song_artists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(Song, null=False)),
            ('artist', models.ForeignKey(Artist, null=False))
        ))
        
        # Adding ManyToManyField 'Artist.groups'
        db.create_table('webview_artist_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('artist', models.ForeignKey(Artist, null=False)),
            ('group', models.ForeignKey(Group, null=False))
        ))
        
        # Adding ManyToManyField 'Song.groups'
        db.create_table('webview_song_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(Song, null=False)),
            ('group', models.ForeignKey(Group, null=False))
        ))
        
        # Creating unique_together for [user, song] on Favorite.
        db.create_unique('webview_favorite', ['user_id', 'song_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Favorite'
        db.delete_table('webview_favorite')
        
        # Deleting model 'News'
        db.delete_table('webview_news')
        
        # Deleting model 'SongComment'
        db.delete_table('webview_songcomment')
        
        # Deleting model 'SongPlatform'
        db.delete_table('webview_songplatform')
        
        # Deleting model 'RadioStream'
        db.delete_table('webview_radiostream')
        
        # Deleting model 'Group'
        db.delete_table('webview_group')
        
        # Deleting model 'AjaxEvent'
        db.delete_table('webview_ajaxevent')
        
        # Deleting model 'SongVote'
        db.delete_table('webview_songvote')
        
        # Deleting model 'PrivateMessage'
        db.delete_table('webview_privatemessage')
        
        # Deleting model 'Oneliner'
        db.delete_table('webview_oneliner')
        
        # Deleting model 'Artist'
        db.delete_table('webview_artist')
        
        # Deleting model 'Queue'
        db.delete_table('webview_queue')
        
        # Deleting model 'SongType'
        db.delete_table('webview_songtype')
        
        # Deleting model 'Logo'
        db.delete_table('webview_logo')
        
        # Deleting model 'UploadTicket'
        db.delete_table('webview_uploadticket')
        
        # Deleting model 'Song'
        db.delete_table('webview_song')
        
        # Deleting model 'Userprofile'
        db.delete_table('webview_userprofile')
        
        # Deleting model 'SongDownload'
        db.delete_table('webview_songdownload')
        
        # Dropping ManyToManyField 'Song.artists'
        db.delete_table('webview_song_artists')
        
        # Dropping ManyToManyField 'Artist.groups'
        db.delete_table('webview_artist_groups')
        
        # Dropping ManyToManyField 'Song.groups'
        db.delete_table('webview_song_groups')
        
        # Deleting unique_together for [user, song] on Favorite.
        db.delete_unique('webview_favorite', ['user_id', 'song_id'])
        
    
    
    models = {
        'webview.favorite': {
            'Meta': {'ordering': "['song']", 'unique_together': '("user","song")'},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'comment': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'webview.news': {
            'Meta': {'ordering': "['-added']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'icon': ('models.URLField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'status': ('models.CharField', [], {'max_length': '1'}),
            'text': ('models.TextField', [], {}),
            'title': ('models.CharField', [], {'max_length': '100'})
        },
        'webview.songcomment': {
            'Meta': {'ordering': "['-added']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'comment': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'webview.queue': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'played': ('models.BooleanField', [], {}),
            'playtime': ('models.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'priority': ('models.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'requested': ('models.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True'}),
            'requested_by': ('models.ForeignKey', ['User'], {}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'time_played': ('models.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'webview.songplatform': {
            'description': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'webview.songdownload': {
            'Meta': {'ordering': "['title']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'download_url': ('models.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'title': ('models.CharField', [], {'max_length': '64'})
        },
        'webview.radiostream': {
            'active': ('models.BooleanField', [], {'default': 'True'}),
            'bitrate': ('models.IntegerField', [], {}),
            'country_code': ('models.CharField', [], {'max_length': '10'}),
            'description': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '120'}),
            'streamtype': ('models.CharField', [], {'max_length': '1'}),
            'url': ('models.CharField', [], {'max_length': '120'})
        },
        'webview.group': {
            'Meta': {'ordering': "['name']"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'}),
            'pouetid': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'webpage': ('models.URLField', [], {'blank': 'True'})
        },
        'webview.ajaxevent': {
            'event': ('models.CharField', [], {'max_length': '100'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'webview.artist': {
            'Meta': {'ordering': "['handle']"},
            'alias_of': ('models.ForeignKey', ["'self'"], {'related_name': "'aliases'", 'null': 'True', 'blank': 'True'}),
            'dob': ('models.DateField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('models.ManyToManyField', ['Group'], {'null': 'True', 'blank': 'True'}),
            'handle': ('models.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'name': ('models.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'webpage': ('models.URLField', [], {'blank': 'True'})
        },
        'webview.privatemessage': {
            'Meta': {'ordering': "['-sent']"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'message': ('models.TextField', [], {}),
            'reply_to': ('models.ForeignKey', ["'PrivateMessage'"], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sender': ('models.ForeignKey', ['User'], {'related_name': '"sent_messages"'}),
            'sent': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'subject': ('models.CharField', [], {'max_length': '60'}),
            'to': ('models.ForeignKey', ['User'], {}),
            'unread': ('models.BooleanField', [], {'default': 'True'})
        },
        'webview.songvote': {
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'user': ('models.ForeignKey', ['User'], {}),
            'vote': ('models.IntegerField', [], {})
        },
        'webview.oneliner': {
            'Meta': {'ordering': "['-added']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'message': ('models.CharField', [], {'max_length': '128'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'webview.songtype': {
            'description': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'webview.logo': {
            'active': ('models.BooleanField', [], {'default': 'True'}),
            'creator': ('models.CharField', [], {'max_length': '60'}),
            'description': ('models.TextField', [], {'blank': 'True'}),
            'file': ('models.FileField', [], {'upload_to': "'media/logos'"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'webview.song': {
            'Meta': {'ordering': "['title']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'artists': ('models.ManyToManyField', ['Artist'], {'null': 'True', 'blank': 'True'}),
            'bitrate': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('models.FileField', [], {'upload_to': "'media/music'"}),
            'groups': ('models.ManyToManyField', ['Group'], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'platform': ('models.ForeignKey', ['SongPlatform'], {'null': 'True', 'blank': 'True'}),
            'pouetid': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rating': ('models.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'rating_total': ('models.IntegerField', [], {'default': '0'}),
            'rating_votes': ('models.IntegerField', [], {'default': '0'}),
            'samplerate': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'song_length': ('models.IntegerField', [], {'null': 'True', 'editable': 'False', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'status': ('models.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'times_played': ('models.IntegerField', [], {'default': '0', 'null': 'True'}),
            'title': ('models.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'type': ('models.ForeignKey', ['SongType'], {'null': 'True', 'verbose_name': "'Source'", 'blank': 'True'}),
            'uploader': ('models.ForeignKey', ['User'], {'null': 'True', 'blank': 'True'})
        },
        'webview.userprofile': {
            'avatar': ('models.ImageField', [], {'null': 'True', 'upload_to': "'media/avatars'", 'blank': 'True'}),
            'country': ('models.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'group': ('models.ForeignKey', ['Group'], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'last_active': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'token': ('models.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'unique': 'True'}),
            'web_page': ('models.URLField', [], {'blank': 'True'})
        },
        'webview.uploadticket': {
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'filename': ('models.CharField', [], {'default': '""', 'max_length': '100', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'tempfile': ('models.CharField', [], {'default': '""', 'max_length': '100', 'blank': 'True'}),
            'ticket': ('models.CharField', [], {'max_length': '20'}),
            'user': ('models.ForeignKey', ['User'], {})
        }
    }
    
    complete_apps = ['webview']
