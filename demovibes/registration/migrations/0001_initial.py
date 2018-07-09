
from south.db import db
from django.db import models
from demovibes.registration.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'RegistrationProfile'
        db.create_table('registration_registrationprofile', (
            ('activation_key', models.CharField(_('activation key'), max_length=40)),
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'], unique=True, verbose_name=_('user'))),
        ))
        db.send_create_signal('registration', ['RegistrationProfile'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'RegistrationProfile'
        db.delete_table('registration_registrationprofile')
        
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'registration.registrationprofile': {
            'activation_key': ('models.CharField', ["_('activation key')"], {'max_length': '40'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'unique': 'True', 'verbose_name': "_('user')"})
        }
    }
    
    complete_apps = ['registration']
