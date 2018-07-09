# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'TagHistory'
        db.create_table('webview_taghistory', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tags', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webview.Song'])),
        ))
        db.send_create_signal('webview', ['TagHistory'])

        # Changing field 'Theme.preview'
        db.alter_column('webview_theme', 'preview', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'News.added'
        db.alter_column('webview_news', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'News.last_updated'
        db.alter_column('webview_news', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True))

        # Changing field 'News.icon'
        db.alter_column('webview_news', 'icon', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'SongType.symbol'
        db.alter_column('webview_songtype', 'symbol', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'SongType.image'
        db.alter_column('webview_songtype', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'RadioStream.active'
        db.alter_column('webview_radiostream', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Group.startswith'
        db.alter_column('webview_group', 'startswith', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Group.last_updated'
        db.alter_column('webview_group', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True))

        # Changing field 'Group.wiki_link'
        db.alter_column('webview_group', 'wiki_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Group.webpage'
        db.alter_column('webview_group', 'webpage', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Group.group_logo'
        db.alter_column('webview_group', 'group_logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Group.group_icon'
        db.alter_column('webview_group', 'group_icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Song.startswith'
        db.alter_column('webview_song', 'startswith', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Song.file'
        db.alter_column('webview_song', 'file', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Changing field 'Song.platform'
        db.alter_column('webview_song', 'platform_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webview.SongPlatform'], null=True, blank=True))

        # Changing field 'Song.hvsc_url'
        db.alter_column('webview_song', 'hvsc_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Song.added'
        db.alter_column('webview_song', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Song.last_changed'
        db.alter_column('webview_song', 'last_changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True))

        # Changing field 'Song.release_year'
        db.alter_column('webview_song', 'release_year', self.gf('django.db.models.fields.CharField')(max_length='4', null=True, blank=True))

        # Changing field 'Song.explicit'
        db.alter_column('webview_song', 'explicit', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'PrivateMessage.visible'
        db.alter_column('webview_privatemessage', 'visible', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'PrivateMessage.reply_to'
        db.alter_column('webview_privatemessage', 'reply_to_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webview.PrivateMessage'], null=True, blank=True))

        # Changing field 'PrivateMessage.unread'
        db.alter_column('webview_privatemessage', 'unread', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'PrivateMessage.sent'
        db.alter_column('webview_privatemessage', 'sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Compilation.purchase_page'
        db.alter_column('webview_compilation', 'purchase_page', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Compilation.cover_art'
        db.alter_column('webview_compilation', 'cover_art', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Compilation.comp_icon'
        db.alter_column('webview_compilation', 'comp_icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Compilation.wiki_link'
        db.alter_column('webview_compilation', 'wiki_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Compilation.download_link'
        db.alter_column('webview_compilation', 'download_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Compilation.youtube_link'
        db.alter_column('webview_compilation', 'youtube_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Compilation.startswith'
        db.alter_column('webview_compilation', 'startswith', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Compilation.date_added'
        db.alter_column('webview_compilation', 'date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Compilation.details_page'
        db.alter_column('webview_compilation', 'details_page', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'SongPlatform.symbol'
        db.alter_column('webview_songplatform', 'symbol', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'SongPlatform.image'
        db.alter_column('webview_songplatform', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Adding field 'Userprofile.use_tags'
        db.add_column('webview_userprofile', 'use_tags', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True), keep_default=False)

        # Changing field 'Userprofile.web_page'
        db.alter_column('webview_userprofile', 'web_page', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Userprofile.pm_accepted_upload'
        db.alter_column('webview_userprofile', 'pm_accepted_upload', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_group_add'
        db.alter_column('webview_userprofile', 'email_on_group_add', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_pm'
        db.alter_column('webview_userprofile', 'email_on_pm', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_artist_add'
        db.alter_column('webview_userprofile', 'email_on_artist_add', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.email_on_artist_comment'
        db.alter_column('webview_userprofile', 'email_on_artist_comment', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Userprofile.custom_css'
        db.alter_column('webview_userprofile', 'custom_css', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Userprofile.avatar'
        db.alter_column('webview_userprofile', 'avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Userprofile.paginate_favorites'
        db.alter_column('webview_userprofile', 'paginate_favorites', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'SongVote.added'
        db.alter_column('webview_songvote', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'CompilationVote.added'
        db.alter_column('webview_compilationvote', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'UploadTicket.added'
        db.alter_column('webview_uploadticket', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'GroupVote.added'
        db.alter_column('webview_groupvote', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Faq.added'
        db.alter_column('webview_faq', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Faq.last_updated'
        db.alter_column('webview_faq', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True))

        # Changing field 'Faq.active'
        db.alter_column('webview_faq', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Link.added'
        db.alter_column('webview_link', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Link.last_updated'
        db.alter_column('webview_link', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True))

        # Changing field 'Link.link_url'
        db.alter_column('webview_link', 'link_url', self.gf('django.db.models.fields.URLField')(max_length=200, unique=True))

        # Changing field 'Link.link_image'
        db.alter_column('webview_link', 'link_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Link.priority'
        db.alter_column('webview_link', 'priority', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Artist.startswith'
        db.alter_column('webview_artist', 'startswith', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Artist.artist_pic'
        db.alter_column('webview_artist', 'artist_pic', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Artist.webpage'
        db.alter_column('webview_artist', 'webpage', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Artist.is_deceased'
        db.alter_column('webview_artist', 'is_deceased', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Artist.last_updated'
        db.alter_column('webview_artist', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True))

        # Changing field 'Artist.alias_of'
        db.alter_column('webview_artist', 'alias_of_id', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, to=orm['webview.Artist']))

        # Changing field 'Artist.wiki_link'
        db.alter_column('webview_artist', 'wiki_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Queue.requested'
        db.alter_column('webview_queue', 'requested', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Queue.played'
        db.alter_column('webview_queue', 'played', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Queue.priority'
        db.alter_column('webview_queue', 'priority', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LinkCategory.icon'
        db.alter_column('webview_linkcategory', 'icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'LinkCategory.id_slug'
        db.alter_column('webview_linkcategory', 'id_slug', self.gf('django.db.models.fields.SlugField')(max_length=50))

        # Changing field 'SongComment.added'
        db.alter_column('webview_songcomment', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Logo.active'
        db.alter_column('webview_logo', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Logo.file'
        db.alter_column('webview_logo', 'file', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Changing field 'Label.startswith'
        db.alter_column('webview_label', 'startswith', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Label.last_updated'
        db.alter_column('webview_label', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True))

        # Changing field 'Label.wiki_link'
        db.alter_column('webview_label', 'wiki_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Label.webpage'
        db.alter_column('webview_label', 'webpage', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True))

        # Changing field 'Label.label_icon'
        db.alter_column('webview_label', 'label_icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Label.logo'
        db.alter_column('webview_label', 'logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Favorite.added'
        db.alter_column('webview_favorite', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'SongApprovals.approved'
        db.alter_column('webview_songapprovals', 'approved', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'Screenshot.startswith'
        db.alter_column('webview_screenshot', 'startswith', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Screenshot.last_updated'
        db.alter_column('webview_screenshot', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True))

        # Changing field 'Screenshot.image'
        db.alter_column('webview_screenshot', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True))

        # Changing field 'Screenshot.active'
        db.alter_column('webview_screenshot', 'active', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Oneliner.added'
        db.alter_column('webview_oneliner', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'SongDownload.added'
        db.alter_column('webview_songdownload', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'ArtistVote.added'
        db.alter_column('webview_artistvote', 'added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))
    
    
    def backwards(self, orm):
        
        # Deleting model 'TagHistory'
        db.delete_table('webview_taghistory')

        # Changing field 'Theme.preview'
        db.alter_column('webview_theme', 'preview', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'News.added'
        db.alter_column('webview_news', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'News.last_updated'
        db.alter_column('webview_news', 'last_updated', self.gf('models.DateTimeField')(null=True, editable=False, blank=True))

        # Changing field 'News.icon'
        db.alter_column('webview_news', 'icon', self.gf('models.URLField')(blank=True))

        # Changing field 'SongType.symbol'
        db.alter_column('webview_songtype', 'symbol', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'SongType.image'
        db.alter_column('webview_songtype', 'image', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'RadioStream.active'
        db.alter_column('webview_radiostream', 'active', self.gf('models.BooleanField')())

        # Changing field 'Group.startswith'
        db.alter_column('webview_group', 'startswith', self.gf('models.CharField')(max_length=1, editable=False))

        # Changing field 'Group.last_updated'
        db.alter_column('webview_group', 'last_updated', self.gf('models.DateTimeField')(null=True, editable=False, blank=True))

        # Changing field 'Group.wiki_link'
        db.alter_column('webview_group', 'wiki_link', self.gf('models.URLField')(blank=True))

        # Changing field 'Group.webpage'
        db.alter_column('webview_group', 'webpage', self.gf('models.URLField')(blank=True))

        # Changing field 'Group.group_logo'
        db.alter_column('webview_group', 'group_logo', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Group.group_icon'
        db.alter_column('webview_group', 'group_icon', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Song.startswith'
        db.alter_column('webview_song', 'startswith', self.gf('models.CharField')(max_length=1, editable=False))

        # Changing field 'Song.file'
        db.alter_column('webview_song', 'file', self.gf('models.FileField')())

        # Changing field 'Song.platform'
        db.alter_column('webview_song', 'platform_id', self.gf('models.ForeignKey')(SongPlatform, null=True, blank=True))

        # Changing field 'Song.hvsc_url'
        db.alter_column('webview_song', 'hvsc_url', self.gf('models.URLField')(blank=True))

        # Changing field 'Song.added'
        db.alter_column('webview_song', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Song.last_changed'
        db.alter_column('webview_song', 'last_changed', self.gf('models.DateTimeField')(auto_now=True))

        # Changing field 'Song.release_year'
        db.alter_column('webview_song', 'release_year', self.gf('models.CharField')(max_length="4", null=True, blank=True))

        # Changing field 'Song.explicit'
        db.alter_column('webview_song', 'explicit', self.gf('models.BooleanField')())

        # Changing field 'PrivateMessage.visible'
        db.alter_column('webview_privatemessage', 'visible', self.gf('models.BooleanField')())

        # Changing field 'PrivateMessage.reply_to'
        db.alter_column('webview_privatemessage', 'reply_to_id', self.gf('models.ForeignKey')('PrivateMessage', null=True, blank=True))

        # Changing field 'PrivateMessage.unread'
        db.alter_column('webview_privatemessage', 'unread', self.gf('models.BooleanField')())

        # Changing field 'PrivateMessage.sent'
        db.alter_column('webview_privatemessage', 'sent', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Compilation.purchase_page'
        db.alter_column('webview_compilation', 'purchase_page', self.gf('models.URLField')(blank=True))

        # Changing field 'Compilation.cover_art'
        db.alter_column('webview_compilation', 'cover_art', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Compilation.comp_icon'
        db.alter_column('webview_compilation', 'comp_icon', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Compilation.wiki_link'
        db.alter_column('webview_compilation', 'wiki_link', self.gf('models.URLField')(blank=True))

        # Changing field 'Compilation.download_link'
        db.alter_column('webview_compilation', 'download_link', self.gf('models.URLField')(blank=True))

        # Changing field 'Compilation.youtube_link'
        db.alter_column('webview_compilation', 'youtube_link', self.gf('models.URLField')(blank=True))

        # Changing field 'Compilation.startswith'
        db.alter_column('webview_compilation', 'startswith', self.gf('models.CharField')(max_length=1, editable=False))

        # Changing field 'Compilation.date_added'
        db.alter_column('webview_compilation', 'date_added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Compilation.details_page'
        db.alter_column('webview_compilation', 'details_page', self.gf('models.URLField')(blank=True))

        # Changing field 'SongPlatform.symbol'
        db.alter_column('webview_songplatform', 'symbol', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'SongPlatform.image'
        db.alter_column('webview_songplatform', 'image', self.gf('models.ImageField')(null=True, blank=True))

        # Deleting field 'Userprofile.use_tags'
        db.delete_column('webview_userprofile', 'use_tags')

        # Changing field 'Userprofile.web_page'
        db.alter_column('webview_userprofile', 'web_page', self.gf('models.URLField')(blank=True))

        # Changing field 'Userprofile.pm_accepted_upload'
        db.alter_column('webview_userprofile', 'pm_accepted_upload', self.gf('models.BooleanField')())

        # Changing field 'Userprofile.email_on_group_add'
        db.alter_column('webview_userprofile', 'email_on_group_add', self.gf('models.BooleanField')())

        # Changing field 'Userprofile.email_on_pm'
        db.alter_column('webview_userprofile', 'email_on_pm', self.gf('models.BooleanField')())

        # Changing field 'Userprofile.email_on_artist_add'
        db.alter_column('webview_userprofile', 'email_on_artist_add', self.gf('models.BooleanField')())

        # Changing field 'Userprofile.email_on_artist_comment'
        db.alter_column('webview_userprofile', 'email_on_artist_comment', self.gf('models.BooleanField')())

        # Changing field 'Userprofile.custom_css'
        db.alter_column('webview_userprofile', 'custom_css', self.gf('models.URLField')(blank=True))

        # Changing field 'Userprofile.avatar'
        db.alter_column('webview_userprofile', 'avatar', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Userprofile.paginate_favorites'
        db.alter_column('webview_userprofile', 'paginate_favorites', self.gf('models.BooleanField')())

        # Changing field 'SongVote.added'
        db.alter_column('webview_songvote', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'CompilationVote.added'
        db.alter_column('webview_compilationvote', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'UploadTicket.added'
        db.alter_column('webview_uploadticket', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'GroupVote.added'
        db.alter_column('webview_groupvote', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Faq.added'
        db.alter_column('webview_faq', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Faq.last_updated'
        db.alter_column('webview_faq', 'last_updated', self.gf('models.DateTimeField')(null=True, editable=False, blank=True))

        # Changing field 'Faq.active'
        db.alter_column('webview_faq', 'active', self.gf('models.BooleanField')())

        # Changing field 'Link.added'
        db.alter_column('webview_link', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Link.last_updated'
        db.alter_column('webview_link', 'last_updated', self.gf('models.DateTimeField')(null=True, editable=False, blank=True))

        # Changing field 'Link.link_url'
        db.alter_column('webview_link', 'link_url', self.gf('models.URLField')(unique=True))

        # Changing field 'Link.link_image'
        db.alter_column('webview_link', 'link_image', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Link.priority'
        db.alter_column('webview_link', 'priority', self.gf('models.BooleanField')())

        # Changing field 'Artist.startswith'
        db.alter_column('webview_artist', 'startswith', self.gf('models.CharField')(max_length=1, editable=False))

        # Changing field 'Artist.artist_pic'
        db.alter_column('webview_artist', 'artist_pic', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Artist.webpage'
        db.alter_column('webview_artist', 'webpage', self.gf('models.URLField')(blank=True))

        # Changing field 'Artist.is_deceased'
        db.alter_column('webview_artist', 'is_deceased', self.gf('models.BooleanField')())

        # Changing field 'Artist.last_updated'
        db.alter_column('webview_artist', 'last_updated', self.gf('models.DateTimeField')(null=True, editable=False, blank=True))

        # Changing field 'Artist.alias_of'
        db.alter_column('webview_artist', 'alias_of_id', self.gf('models.ForeignKey')('self', null=True, blank=True))

        # Changing field 'Artist.wiki_link'
        db.alter_column('webview_artist', 'wiki_link', self.gf('models.URLField')(blank=True))

        # Changing field 'Queue.requested'
        db.alter_column('webview_queue', 'requested', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Queue.played'
        db.alter_column('webview_queue', 'played', self.gf('models.BooleanField')())

        # Changing field 'Queue.priority'
        db.alter_column('webview_queue', 'priority', self.gf('models.BooleanField')())

        # Changing field 'LinkCategory.icon'
        db.alter_column('webview_linkcategory', 'icon', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'LinkCategory.id_slug'
        db.alter_column('webview_linkcategory', 'id_slug', self.gf('models.SlugField')(_("Slug")))

        # Changing field 'SongComment.added'
        db.alter_column('webview_songcomment', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Logo.active'
        db.alter_column('webview_logo', 'active', self.gf('models.BooleanField')())

        # Changing field 'Logo.file'
        db.alter_column('webview_logo', 'file', self.gf('models.FileField')())

        # Changing field 'Label.startswith'
        db.alter_column('webview_label', 'startswith', self.gf('models.CharField')(max_length=1, editable=False))

        # Changing field 'Label.last_updated'
        db.alter_column('webview_label', 'last_updated', self.gf('models.DateTimeField')(null=True, editable=False, blank=True))

        # Changing field 'Label.wiki_link'
        db.alter_column('webview_label', 'wiki_link', self.gf('models.URLField')(blank=True))

        # Changing field 'Label.webpage'
        db.alter_column('webview_label', 'webpage', self.gf('models.URLField')(blank=True))

        # Changing field 'Label.label_icon'
        db.alter_column('webview_label', 'label_icon', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Label.logo'
        db.alter_column('webview_label', 'logo', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Favorite.added'
        db.alter_column('webview_favorite', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'SongApprovals.approved'
        db.alter_column('webview_songapprovals', 'approved', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'Screenshot.startswith'
        db.alter_column('webview_screenshot', 'startswith', self.gf('models.CharField')(max_length=1, editable=False))

        # Changing field 'Screenshot.last_updated'
        db.alter_column('webview_screenshot', 'last_updated', self.gf('models.DateTimeField')(null=True, editable=False, blank=True))

        # Changing field 'Screenshot.image'
        db.alter_column('webview_screenshot', 'image', self.gf('models.ImageField')(null=True, blank=True))

        # Changing field 'Screenshot.active'
        db.alter_column('webview_screenshot', 'active', self.gf('models.BooleanField')())

        # Changing field 'Oneliner.added'
        db.alter_column('webview_oneliner', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'SongDownload.added'
        db.alter_column('webview_songdownload', 'added', self.gf('models.DateTimeField')(auto_now_add=True))

        # Changing field 'ArtistVote.added'
        db.alter_column('webview_artistvote', 'added', self.gf('models.DateTimeField')(auto_now_add=True))
    
    
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True', 'db_index': 'True'}),
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
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
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
            'pouetid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'projecttwosix_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'rating_total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rating_votes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'release_year': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': "'4'", 'null': 'True', 'blank': 'True'}),
            'remix_of_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'webview.songdownload': {
            'Meta': {'object_name': 'SongDownload'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webview.Song']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
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
            'last_activity': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'paginate_favorites': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'pm_accepted_upload': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
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
