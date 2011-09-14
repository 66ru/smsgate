# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GateSettings'
        db.create_table('smsgate_gatesettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gate_module', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('config', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('smsgate', ['GateSettings'])

        # Adding model 'Partner'
        db.create_table('smsgate_partner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='partner', unique=True, to=orm['auth.User'])),
            ('token', self.gf('django.db.models.fields.CharField')(default='2MW7CxOGJ76ydzrLPtGA', unique=True, max_length=20)),
            ('sms_from', self.gf('django.db.models.fields.CharField')(max_length=11, blank=True)),
            ('gate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smsgate.GateSettings'])),
        ))
        db.send_create_signal('smsgate', ['Partner'])

        # Adding model 'IPRange'
        db.create_table('smsgate_iprange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_from', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('ip_to', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('partner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ips_allowed', to=orm['smsgate.Partner'])),
        ))
        db.send_create_signal('smsgate', ['IPRange'])

        # Adding model 'QueueItem'
        db.create_table('smsgate_queueitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone_n', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('partner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smsgate.Partner'])),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('status_message', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('smsgate', ['QueueItem'])

        # Adding model 'SmsLog'
        db.create_table('smsgate_smslog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smsgate.QueueItem'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('smsgate', ['SmsLog'])


    def backwards(self, orm):
        
        # Deleting model 'GateSettings'
        db.delete_table('smsgate_gatesettings')

        # Deleting model 'Partner'
        db.delete_table('smsgate_partner')

        # Deleting model 'IPRange'
        db.delete_table('smsgate_iprange')

        # Deleting model 'QueueItem'
        db.delete_table('smsgate_queueitem')

        # Deleting model 'SmsLog'
        db.delete_table('smsgate_smslog')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'smsgate.gatesettings': {
            'Meta': {'object_name': 'GateSettings'},
            'config': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gate_module': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'smsgate.iprange': {
            'Meta': {'object_name': 'IPRange'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_from': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'ip_to': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ips_allowed'", 'to': "orm['smsgate.Partner']"})
        },
        'smsgate.partner': {
            'Meta': {'object_name': 'Partner'},
            'gate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smsgate.GateSettings']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sms_from': ('django.db.models.fields.CharField', [], {'max_length': '11', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'ub9u76xNSoe8aRgT3FcI'", 'unique': 'True', 'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'partner'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'smsgate.queueitem': {
            'Meta': {'object_name': 'QueueItem'},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smsgate.Partner']"}),
            'phone_n': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'status_message': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'smsgate.smslog': {
            'Meta': {'object_name': 'SmsLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smsgate.QueueItem']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['smsgate']
