
from south.db import db
from django.db import models
from demovibes.webview.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Song.wos_id'
        db.alter_column('webview_song', 'wos_id', models.CharField(verbose_name="W.O.S. ID", max_length=8, null=True, blank=True))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Song.wos_id'
        db.alter_column('webview_song', 'wos_id', models.IntegerField(null=True, verbose_name="W.O.S. ID", blank=True))
        
    
    
    models = {
        'webview.theme': {
            'css': ('models.CharField', [], {'max_length': '120'}),
            'description': ('models.TextField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'preview': ('models.ImageField', [], {'null': 'True', 'upload_to': "'media/theme_preview'", 'blank': 'True'}),
            'title': ('models.CharField', [], {'max_length': '20'})
        },
        'webview.news': {
            'Meta': {'ordering': "['-added']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True'}),
            'icon': ('models.URLField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'status': ('models.CharField', [], {'max_length': '1'}),
            'text': ('models.TextField', [], {}),
            'title': ('models.CharField', [], {'max_length': '100'})
        },
        'webview.songtype': {
            'description': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'webview.radiostream': {
            'active': ('models.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'bitrate': ('models.IntegerField', [], {}),
            'country_code': ('models.CharField', [], {'max_length': '10'}),
            'description': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '120'}),
            'streamtype': ('models.CharField', [], {'max_length': '1'}),
            'url': ('models.CharField', [], {'max_length': '120'})
        },
        'webview.countrylist': {
            'Meta': {'ordering': "['name']"},
            'code': ('models.CharField', [], {'max_length': '20'}),
            'flag': ('models.CharField', [], {'max_length': '20'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '60'})
        },
        'webview.group': {
            'Meta': {'ordering': "['name']"},
            'created_by': ('models.ForeignKey', ['User'], {'related_name': '"group_createdby"', 'null': 'True', 'blank': 'True'}),
            'found_date': ('models.DateField', [], {'null': 'True', 'verbose_name': '"Found Date"', 'blank': 'True'}),
            'group_logo': ('models.ImageField', [], {'null': 'True', 'upload_to': "'media/groups'", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'verbose_name': '"Group Info"', 'blank': 'True'}),
            'last_updated': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '30', 'verbose_name': '"* Name"', 'db_index': 'True'}),
            'pouetid': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"Pouet ID"', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'status': ('models.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'webpage': ('models.URLField', [], {'verbose_name': '"Website"', 'blank': 'True'}),
            'wiki_link': ('models.URLField', [], {'blank': 'True'})
        },
        'webview.oneliner': {
            'Meta': {'ordering': "['-added']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'message': ('models.CharField', [], {'max_length': '256'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'webview.song': {
            'Meta': {'ordering': "['title']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'artists': ('models.ManyToManyField', ['Artist'], {'null': 'True', 'blank': 'True'}),
            'bitrate': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('models.FileField', [], {'verbose_name': '"File"', 'upload_to': "'media/music'"}),
            'groups': ('models.ManyToManyField', ['Group'], {'null': 'True', 'blank': 'True'}),
            'hvsc_url': ('models.URLField', [], {'verbose_name': '"HVSC Link"', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'labels': ('models.ManyToManyField', ['Label'], {'null': 'True', 'blank': 'True'}),
            'lemon_id': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"Lemon64 ID"', 'blank': 'True'}),
            'locked_until': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'num_favorited': ('models.IntegerField', [], {'default': '0'}),
            'platform': ('models.ForeignKey', ['SongPlatform'], {'null': 'True', 'blank': 'True'}),
            'pouetid': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'projecttwosix_id': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"Project2612 ID"', 'blank': 'True'}),
            'rating': ('models.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'rating_total': ('models.IntegerField', [], {'default': '0'}),
            'rating_votes': ('models.IntegerField', [], {'default': '0'}),
            'release_date': ('models.DateTimeField', [], {'null': 'True', 'verbose_name': '"Release Date"', 'blank': 'True'}),
            'remix_of_id': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"Mix SongID"', 'blank': 'True'}),
            'samplerate': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'song_length': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'status': ('models.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'times_played': ('models.IntegerField', [], {'default': '0', 'null': 'True'}),
            'title': ('models.CharField', [], {'max_length': '80', 'verbose_name': '"* Song Name"', 'db_index': 'True'}),
            'type': ('models.ForeignKey', ['SongType'], {'null': 'True', 'verbose_name': "'Source'", 'blank': 'True'}),
            'uploader': ('models.ForeignKey', ['User'], {'null': 'True', 'blank': 'True'}),
            'wos_id': ('models.CharField', [], {'verbose_name': '"W.O.S. ID"', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'zxdemo_id': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"ZXDemo ID"', 'blank': 'True'})
        },
        'webview.compilation': {
            'Meta': {'ordering': "['name']"},
            'bar_code': ('models.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'cover_art': ('models.ImageField', [], {'null': 'True', 'upload_to': "'media/compilations'", 'blank': 'True'}),
            'created_by': ('models.ForeignKey', ['User'], {'null': 'True', 'blank': 'True'}),
            'date_added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'details_page': ('models.URLField', [], {'blank': 'True'}),
            'download_link': ('models.URLField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'label': ('models.CharField', [], {'max_length': '30', 'verbose_name': '"Prod. Label"', 'blank': 'True'}),
            'last_updated': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'media_format': ('models.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '30', 'verbose_name': '"* Name"', 'db_index': 'True'}),
            'num_discs': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pouet': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'prod_artists': ('models.ManyToManyField', ['Artist'], {'null': 'True', 'verbose_name': '"Production Artists"', 'blank': 'True'}),
            'prod_groups': ('models.ManyToManyField', ['Group'], {'null': 'True', 'verbose_name': '"Production Groups"', 'blank': 'True'}),
            'prod_notes': ('models.TextField', [], {'blank': 'True'}),
            'projecttwosix_id': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"Project2612 ID"', 'blank': 'True'}),
            'purchase_page': ('models.URLField', [], {'blank': 'True'}),
            'rel_date': ('models.DateField', [], {'null': 'True', 'blank': 'True'}),
            'running_time': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'songs': ('models.ManyToManyField', ['Song'], {'null': 'True', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'status': ('models.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'wiki_link': ('models.URLField', [], {'blank': 'True'}),
            'youtube_link': ('models.URLField', [], {'blank': 'True'}),
            'zxdemo_id': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"ZXDemo ID"', 'blank': 'True'})
        },
        'webview.songplatform': {
            'description': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'webview.userprofile': {
            'aol_id': ('models.CharField', [], {'max_length': '40', 'verbose_name': '"AOL IM"', 'blank': 'True'}),
            'avatar': ('models.ImageField', [], {'null': 'True', 'upload_to': "'media/avatars'", 'blank': 'True'}),
            'country': ('models.CharField', [], {'max_length': '10', 'verbose_name': '"Country code"', 'blank': 'True'}),
            'custom_css': ('models.URLField', [], {'blank': 'True'}),
            'email_on_artist_add': ('models.BooleanField', [], {'default': 'True', 'verbose_name': '"Send email on artist approval"'}),
            'email_on_artist_comment': ('models.BooleanField', [], {'default': 'True', 'verbose_name': '"Send email on artist comments"'}),
            'email_on_group_add': ('models.BooleanField', [], {'default': 'True', 'verbose_name': '"Send email on group approval"'}),
            'email_on_pm': ('models.BooleanField', [], {'default': 'False', 'verbose_name': '"Send email on new PM"'}),
            'fave_id': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"Fave SongID"', 'blank': 'True'}),
            'group': ('models.ForeignKey', ['Group'], {'null': 'True', 'blank': 'True'}),
            'icq_id': ('models.CharField', [], {'max_length': '40', 'verbose_name': '"ICQ Number"', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'verbose_name': '"Profile Info"', 'blank': 'True'}),
            'infoline': ('models.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'last_active': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_activity': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('models.CharField', [], {'max_length': '40', 'verbose_name': '"Hometown Location"', 'blank': 'True'}),
            'paginate_favorites': ('models.BooleanField', [], {'default': 'True'}),
            'pm_accepted_upload': ('models.BooleanField', [], {'default': 'True', 'verbose_name': '"Send PM on accepted upload"'}),
            'real_name': ('models.CharField', [], {'max_length': '40', 'verbose_name': '"Real Name"', 'blank': 'True'}),
            'theme': ('models.ForeignKey', ['Theme'], {'null': 'True', 'blank': 'True'}),
            'token': ('models.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'unique': 'True'}),
            'visible_to': ('models.CharField', [], {'default': '"A"', 'max_length': '1'}),
            'web_page': ('models.URLField', [], {'verbose_name': '"Website"', 'blank': 'True'}),
            'yahoo_id': ('models.CharField', [], {'max_length': '40', 'verbose_name': '"Yahoo! ID"', 'blank': 'True'})
        },
        'webview.ajaxevent': {
            'event': ('models.CharField', [], {'max_length': '100'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'webview.songvote': {
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'user': ('models.ForeignKey', ['User'], {}),
            'vote': ('models.IntegerField', [], {})
        },
        'webview.compilationvote': {
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'comp': ('models.ForeignKey', ['Compilation'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['User'], {}),
            'vote': ('models.IntegerField', [], {'default': '0'})
        },
        'webview.uploadticket': {
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'filename': ('models.CharField', [], {'default': '""', 'max_length': '100', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'tempfile': ('models.CharField', [], {'default': '""', 'max_length': '100', 'blank': 'True'}),
            'ticket': ('models.CharField', [], {'max_length': '20'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'webview.groupvote': {
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'group': ('models.ForeignKey', ['Group'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['User'], {}),
            'vote': ('models.IntegerField', [], {'default': '0'})
        },
        'webview.artist': {
            'Meta': {'ordering': "['handle']"},
            'alias_of': ('models.ForeignKey', ["'self'"], {'related_name': "'aliases'", 'null': 'True', 'blank': 'True'}),
            'artist_pic': ('models.ImageField', [], {'upload_to': "'media/artists'", 'null': 'True', 'verbose_name': '"Picture"', 'blank': 'True'}),
            'created_by': ('models.ForeignKey', ['User'], {'related_name': '"artist_createdby"', 'null': 'True', 'blank': 'True'}),
            'dob': ('models.DateField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('models.ManyToManyField', ['Group'], {'null': 'True', 'blank': 'True'}),
            'handle': ('models.CharField', [], {'unique': 'True', 'max_length': '64', 'verbose_name': '"* Handle"', 'db_index': 'True'}),
            'home_country': ('models.CharField', [], {'max_length': '10', 'verbose_name': '"Country Code"', 'blank': 'True'}),
            'home_location': ('models.CharField', [], {'max_length': '40', 'verbose_name': '"Location"', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'labels': ('models.ManyToManyField', ['Label'], {'null': 'True', 'blank': 'True'}),
            'last_fm_id': ('models.CharField', [], {'max_length': '32', 'verbose_name': '"Last.fm ID"', 'blank': 'True'}),
            'last_updated': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link_to_user': ('models.OneToOneField', ['User'], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', [], {'max_length': '64', 'verbose_name': '"Name"', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'status': ('models.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'webpage': ('models.URLField', [], {'verbose_name': '"Website"', 'blank': 'True'}),
            'wiki_link': ('models.URLField', [], {'blank': 'True'})
        },
        'webview.queue': {
            'eta': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'played': ('models.BooleanField', [], {}),
            'playtime': ('models.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'priority': ('models.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'requested': ('models.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True'}),
            'requested_by': ('models.ForeignKey', ['User'], {}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'time_played': ('models.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'webview.songcomment': {
            'Meta': {'ordering': "['-added']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'comment': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'webview.logo': {
            'active': ('models.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'creator': ('models.CharField', [], {'max_length': '60'}),
            'description': ('models.TextField', [], {'blank': 'True'}),
            'file': ('models.FileField', [], {'upload_to': "'media/logos'"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'webview.label': {
            'Meta': {'ordering': "['name']"},
            'cease_date': ('models.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_by': ('models.ForeignKey', ['User'], {'related_name': '"label_createdby"', 'null': 'True', 'blank': 'True'}),
            'found_date': ('models.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'info': ('models.TextField', [], {'blank': 'True'}),
            'last_updated': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'logo': ('models.ImageField', [], {'verbose_name': '"Label Logo"', 'null': 'True', 'upload_to': "'media/labels'", 'blank': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '40', 'verbose_name': '"* Name"', 'db_index': 'True'}),
            'pouetid': ('models.IntegerField', [], {'null': 'True', 'verbose_name': '"Pouet ID"', 'blank': 'True'}),
            'startswith': ('models.CharField', [], {'max_length': '1', 'editable': 'False', 'db_index': 'True'}),
            'status': ('models.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'webpage': ('models.URLField', [], {'verbose_name': '"Website"', 'blank': 'True'}),
            'wiki_link': ('models.URLField', [], {'blank': 'True'})
        },
        'webview.favorite': {
            'Meta': {'ordering': "['song']", 'unique_together': '("user","song")'},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'comment': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'webview.songapprovals': {
            'approved': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'approved_by': ('models.ForeignKey', ['User'], {'related_name': '"uploadlist_approvedby"'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'uploaded_by': ('models.ForeignKey', ['User'], {'related_name': '"uploadlist_uploadedby"'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
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
            'unread': ('models.BooleanField', [], {'default': 'True'}),
            'visible': ('models.BooleanField', [], {'default': 'True', 'db_index': 'True'})
        },
        'webview.songdownload': {
            'Meta': {'ordering': "['title']"},
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'download_url': ('models.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'song': ('models.ForeignKey', ['Song'], {}),
            'title': ('models.CharField', [], {'max_length': '64'})
        },
        'webview.artistvote': {
            'added': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'artist': ('models.ForeignKey', ['Artist'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['User'], {}),
            'vote': ('models.IntegerField', [], {'default': '0'})
        }
    }
    
    complete_apps = ['webview']
