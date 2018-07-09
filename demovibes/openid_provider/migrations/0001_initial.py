# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from openid_provider.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'TrustedRoot'
        db.create_table('openid_provider_trustedroot', (
            ('openid', models.ForeignKey(orm.OpenID)),
            ('trust_root', models.CharField(max_length=200)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('openid_provider', ['TrustedRoot'])
        
        # Adding model 'OpenID'
        db.create_table('openid_provider_openid', (
            ('default', models.BooleanField(default=False)),
            ('openid', models.CharField(unique=True, max_length=200, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'])),
        ))
        db.send_create_signal('openid_provider', ['OpenID'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'TrustedRoot'
        db.delete_table('openid_provider_trustedroot')
        
        # Deleting model 'OpenID'
        db.delete_table('openid_provider_openid')
        
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
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
        }
    }
    
    complete_apps = ['openid_provider']
