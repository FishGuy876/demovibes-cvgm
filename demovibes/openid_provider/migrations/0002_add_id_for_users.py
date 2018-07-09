# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from openid_provider.models import *
import datetime

class Migration:
    
    no_dry_run = True

    def forwards(self, orm):
        "Write your forwards migration here"
        for u in orm['auth.User'].objects.all():
            u.openid_set.create(openid = u.username)
            print "Created OpenID for %s" % u.username
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'auth.message': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'message': ('models.TextField', ["_('message')"], {}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'auth.user': {
            'date_joined': ('models.DateTimeField', ["_('date joined')"], {'default': 'datetime.datetime.now'}),
            'email': ('models.EmailField', ["_('e-mail address')"], {'blank': 'True'}),
            'first_name': ('models.CharField', ["_('first name')"], {'max_length': '30', 'blank': 'True'}),
            'groups': ('models.ManyToManyField', ['Group'], {'verbose_name': "_('groups')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('models.BooleanField', ["_('active')"], {'default': 'True'}),
            'is_staff': ('models.BooleanField', ["_('staff status')"], {'default': 'False'}),
            'is_superuser': ('models.BooleanField', ["_('superuser status')"], {'default': 'False'}),
            'last_login': ('models.DateTimeField', ["_('last login')"], {'default': 'datetime.datetime.now'}),
            'last_name': ('models.CharField', ["_('last name')"], {'max_length': '30', 'blank': 'True'}),
            'password': ('models.CharField', ["_('password')"], {'max_length': '128'}),
            'user_permissions': ('models.ManyToManyField', ['Permission'], {'verbose_name': "_('user permissions')", 'blank': 'True'}),
            'username': ('models.CharField', ["_('username')"], {'unique': 'True', 'max_length': '30'})
        },
        'openid_provider.trustedroot': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'openid': ('models.ForeignKey', ['OpenID'], {}),
            'trust_root': ('models.CharField', [], {'max_length': '200'})
        },
        'openid_provider.openid': {
            'Meta': {'ordering': "['openid']"},
            'default': ('models.BooleanField', [], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'openid': ('models.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label','codename')", 'unique_together': "(('content_type','codename'),)"},
            'codename': ('models.CharField', ["_('codename')"], {'max_length': '100'}),
            'content_type': ('models.ForeignKey', ['ContentType'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('name')"], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'auth.group': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('name')"], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('models.ManyToManyField', ['Permission'], {'verbose_name': "_('permissions')", 'blank': 'True'})
        }
    }
    
    complete_apps = ['openid_provider', 'auth']
