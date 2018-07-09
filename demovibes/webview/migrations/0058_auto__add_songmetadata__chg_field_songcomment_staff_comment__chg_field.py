# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'SongMetaData'
        db.create_table('webview_songmetadata', (
            ('info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('checked', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('release_year', self.gf('django.db.models.fields.CharField')(db_index=True, max_length='4', null=True, blank=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webview.Song'])),
            ('platform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webview.SongPlatform'], null=True, blank=True)),
            ('remix_of_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webview.SongType'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('webview', ['SongMetaData'])

        # Adding M2M table for field labels on 'SongMetaData'
        db.create_table('webview_songmetadata_labels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('songmetadata', models.ForeignKey(orm['webview.songmetadata'], null=False)),
            ('label', models.ForeignKey(orm['webview.label'], null=False))
        ))
        db.create_unique('webview_songmetadata_labels', ['songmetadata_id', 'label_id'])

        # Adding M2M table for field groups on 'SongMetaData'
        db.create_table('webview_songmetadata_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('songmetadata', models.ForeignKey(orm['webview.songmetadata'], null=False)),
            ('group', models.ForeignKey(orm['webview.group'], null=False))
        ))
        db.create_unique('webview_songmetadata_groups', ['songmetadata_id', 'group_id'])

        # Adding M2M table for field artists on 'SongMetaData'
        db.create_table('webview_songmetadata_artists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('songmetadata', models.ForeignKey(orm['webview.songmetadata'], null=False)),
            ('artist', models.ForeignKey(orm['webview.artist'], null=False))
        ))
        db.create_unique('webview_songmetadata_artists', ['songmetadata_id', 'artist_id'])

        # Changing field 'SongComment.staff_comment'
        db.alter_column('webview_songcomment', 'staff_comment', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'RadioStream.active'
        db.alter_column('webview_radiostream', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Song.explicit'
        db.alter_column('webview_song', 'explicit', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Faq.active'
        db.alter_column('webview_faq', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Link.priority'
        db.alter_column('webview_link', 'priority', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Artist.is_deceased'
        db.alter_column('webview_artist', 'is_deceased', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Queue.played'
        db.alter_column('webview_queue', 'played', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Queue.priority'
        db.alter_column('webview_queue', 'priority', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Logo.active'
        db.alter_column('webview_logo', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.pm_accepted_upload'
        db.alter_column('webview_userprofile', 'pm_accepted_upload', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_group_add'
        db.alter_column('webview_userprofile', 'email_on_group_add', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_pm'
        db.alter_column('webview_userprofile', 'email_on_pm', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_artist_add'
        db.alter_column('webview_userprofile', 'email_on_artist_add', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.show_youtube'
        db.alter_column('webview_userprofile', 'show_youtube', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_artist_comment'
        db.alter_column('webview_userprofile', 'email_on_artist_comment', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.use_tags'
        db.alter_column('webview_userprofile', 'use_tags', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.paginate_favorites'
        db.alter_column('webview_userprofile', 'paginate_favorites', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Screenshot.active'
        db.alter_column('webview_screenshot', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'PrivateMessage.visible'
        db.alter_column('webview_privatemessage', 'visible', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'PrivateMessage.unread'
        db.alter_column('webview_privatemessage', 'unread', self.gf('django.db.models.fields.BooleanField')(blank=True))
    
    
    def backwards(self, orm):
        
        # Deleting model 'SongMetaData'
        db.delete_table('webview_songmetadata')

        # Removing M2M table for field labels on 'SongMetaData'
        db.delete_table('webview_songmetadata_labels')

        # Removing M2M table for field groups on 'SongMetaData'
        db.delete_table('webview_songmetadata_groups')

        # Removing M2M table for field artists on 'SongMetaData'
        db.delete_table('webview_songmetadata_artists')

        # Changing field 'SongComment.staff_comment'
        db.alter_column('webview_songcomment', 'staff_comment', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'RadioStream.active'
        db.alter_column('webview_radiostream', 'active', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Song.explicit'
        db.alter_column('webview_song', 'explicit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Faq.active'
        db.alter_column('webview_faq', 'active', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Link.priority'
        db.alter_column('webview_link', 'priority', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Artist.is_deceased'
        db.alter_column('webview_artist', 'is_deceased', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Queue.played'
        db.alter_column('webview_queue', 'played', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Queue.priority'
        db.alter_column('webview_queue', 'priority', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Logo.active'
        db.alter_column('webview_logo', 'active', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.pm_accepted_upload'
        db.alter_column('webview_userprofile', 'pm_accepted_upload', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.email_on_group_add'
        db.alter_column('webview_userprofile', 'email_on_group_add', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.email_on_pm'
        db.alter_column('webview_userprofile', 'email_on_pm', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.email_on_artist_add'
        db.alter_column('webview_userprofile', 'email_on_artist_add', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.show_youtube'
        db.alter_column('webview_userprofile', 'show_youtube', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.email_on_artist_comment'
        db.alter_column('webview_userprofile', 'email_on_artist_comment', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.use_tags'
        db.alter_column('webview_userprofile', 'use_tags', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Userprofile.paginate_favorites'
        db.alter_column('webview_userprofile', 'paginate_favorites', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Screenshot.active'
        db.alter_column('webview_screenshot', 'active', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'PrivateMessage.visible'
        db.alter_column('webview_privatemessage', 'visible', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'PrivateMessage.unread'
        db.alter_column('webview_privatemessage', 'unread', self.gf('django.db.models.fields.BooleanField')())
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'webview.ajaxevent': {
            'Meta': {'object_name': 'AjaxEvent'},
            'event': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'webview.artist': {
            'Meta': {'object_name': 'Artist'},
            'alias_of': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'blank': 'True', 'null': 'True', 'to': "orm['webview.Artist']"}),
            'artist_pic': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'artist_createdby'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'deceased_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Group']", 'null': 'True', 'blank': 'True'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '64', 'unique': 'True', 'db_index': 'True'}),
            'hol_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'home_country': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'home_location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'is_deceased': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Label']", 'null': 'True', 'blank': 'True'}),
            'last_fm_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link_to_user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'startswith': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'webpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'webview.artistvote': {
            'Meta': {'object_name': 'ArtistVote'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Artist']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'webview.compilation': {
            'Meta': {'object_name': 'Compilation'},
            'bar_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'comp_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cover_art': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'details_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'download_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'hol_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'media_format': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'db_index': 'True'}),
            'num_discs': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pouet': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'prod_artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Artist']", 'null': 'True', 'blank': 'True'}),
            'prod_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Group']", 'null': 'True', 'blank': 'True'}),
            'prod_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'projecttwosix_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'purchase_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'rel_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'running_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'songs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Song']", 'null': 'True', 'blank': 'True'}),
            'startswith': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'wiki_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'youtube_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zxdemo_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'webview.compilationvote': {
            'Meta': {'object_name': 'CompilationVote'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Compilation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'webview.countrylist': {
            'Meta': {'object_name': 'CountryList'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'flag': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'webview.faq': {
            'Meta': {'object_name': 'Faq'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'answer': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'webview.favorite': {
            'Meta': {'unique_together': "(('user', 'song'),)", 'object_name': 'Favorite'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'webview.genericbaselink': {
            'Meta': {'object_name': 'GenericBaseLink'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inputinfo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'linktype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'regex': ('django.db.models.fields.TextField', [], {})
        },
        'webview.genericlink': {
            'Meta': {'object_name': 'GenericLink'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.GenericBaseLink']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'webview.group': {
            'Meta': {'object_name': 'Group'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_createdby'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'found_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'group_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'group_logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'db_index': 'True'}),
            'pouetid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'startswith': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'webpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'webview.groupvote': {
            'Meta': {'object_name': 'GroupVote'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'webview.label': {
            'Meta': {'object_name': 'Label'},
            'cease_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'label_createdby'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'found_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hol_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'label_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'unique': 'True', 'db_index': 'True'}),
            'pouetid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'startswith': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'webpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'webview.link': {
            'Meta': {'object_name': 'Link'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'label_approvedby'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'link_title': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'link_type': ('django.db.models.fields.CharField', [], {'default': "'T'", 'max_length': '1'}),
            'link_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'unique': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1', 'db_index': 'True'}),
            'submitted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'label_submittedby'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'url_cat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.LinkCategory']"})
        },
        'webview.linkcategory': {
            'Meta': {'object_name': 'LinkCategory'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'webview.logo': {
            'Meta': {'object_name': 'Logo'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'webview.news': {
            'Meta': {'object_name': 'News'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'webview.oneliner': {
            'Meta': {'object_name': 'Oneliner'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'webview.privatemessage': {
            'Meta': {'object_name': 'PrivateMessage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'reply_to': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['webview.PrivateMessage']", 'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': "orm['auth.User']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'to': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'unread': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'webview.queue': {
            'Meta': {'object_name': 'Queue'},
            'eta': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'played': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'playtime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'requested': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'requested_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'time_played': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'webview.radiostream': {
            'Meta': {'object_name': 'RadioStream'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'streamtype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'webview.screenshot': {
            'Meta': {'object_name': 'Screenshot'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'screenshoit_addedby'", 'blank': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70', 'unique': 'True'}),
            'startswith': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'})
        },
        'webview.song': {
            'Meta': {'object_name': 'Song'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'al_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Artist']", 'null': 'True', 'blank': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cvgm_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dtv_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'explicit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '200'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Group']", 'null': 'True', 'blank': 'True'}),
            'hol_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hvsc_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Label']", 'null': 'True', 'blank': 'True'}),
            'last_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'lemon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'locked_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'loopfade_time': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'necta_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_favorited': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'platform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.SongPlatform']", 'null': 'True', 'blank': 'True'}),
            'pouetgroup': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'pouetid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pouetlink': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'pouetss': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'pouettitle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'projecttwosix_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'rating_total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rating_votes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'release_year': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': "'4'", 'null': 'True', 'blank': 'True'}),
            'remix_of_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'replay_gain': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'samplerate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'song_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'startswith': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'times_played': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80', 'db_index': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.SongType']", 'null': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'wos_id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'ytvidid': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'ytvidoffset': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'zxdemo_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'webview.songapprovals': {
            'Meta': {'object_name': 'SongApprovals'},
            'approved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploadlist_approvedby'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'uploaded_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploadlist_uploadedby'", 'to': "orm['auth.User']"})
        },
        'webview.songcomment': {
            'Meta': {'object_name': 'SongComment'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'staff_comment': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'webview.songdownload': {
            'Meta': {'object_name': 'SongDownload'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'webview.songmetadata': {
            'Meta': {'object_name': 'SongMetaData'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'artists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Artist']", 'null': 'True', 'blank': 'True'}),
            'checked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['webview.Label']", 'null': 'True', 'blank': 'True'}),
            'platform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.SongPlatform']", 'null': 'True', 'blank': 'True'}),
            'release_year': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': "'4'", 'null': 'True', 'blank': 'True'}),
            'remix_of_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.SongType']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'webview.songplatform': {
            'Meta': {'object_name': 'SongPlatform'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'symbol': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'unique': 'True'})
        },
        'webview.songtype': {
            'Meta': {'object_name': 'SongType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'symbol': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'unique': 'True'})
        },
        'webview.songvote': {
            'Meta': {'object_name': 'SongVote'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {})
        },
        'webview.taghistory': {
            'Meta': {'object_name': 'TagHistory'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'tags': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'webview.theme': {
            'Meta': {'object_name': 'Theme'},
            'css': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'webview.uploadticket': {
            'Meta': {'object_name': 'UploadTicket'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tempfile': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'webview.userprofile': {
            'Meta': {'object_name': 'Userprofile'},
            'aol_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'custom_css': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'email_on_artist_add': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'email_on_artist_comment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'email_on_group_add': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'email_on_pm': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'fave_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Group']", 'null': 'True', 'blank': 'True'}),
            'hol_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'icq_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'infoline': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'last_active': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_activity': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'last_changed': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 11, 28, 3, 0, 40, 470956)'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'paginate_favorites': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'pm_accepted_upload': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'show_youtube': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Theme']", 'null': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'use_tags': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'visible_to': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'yahoo_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        }
    }
    
    complete_apps = ['webview']
