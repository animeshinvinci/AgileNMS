# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Group'
        db.create_table(u'monitoring_group', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('notification_addresses', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'monitoring', ['Group'])

        # Adding model 'Check'
        db.create_table(u'monitoring_check', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitoring.Group'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('notification_addresses', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('maintenance_mode', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'monitoring', ['Check'])

        # Adding model 'CheckDailyReport'
        db.create_table(u'monitoring_checkdailyreport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitoring.Check'])),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('update_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status_ok', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status_warning', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status_critical', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status_unknown', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status_disabled', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maintenance_mode', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'monitoring', ['CheckDailyReport'])

        # Adding model 'Problem'
        db.create_table(u'monitoring_problem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitoring.Check'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('acknowledged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('send_down_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('send_up_email', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'monitoring', ['Problem'])

        # Adding model 'Report'
        db.create_table(u'monitoring_report', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('schedule', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('start_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('notification_addresses', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'monitoring', ['Report'])

        # Adding M2M table for field checks on 'Report'
        m2m_table_name = db.shorten_name(u'monitoring_report_checks')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('report', models.ForeignKey(orm[u'monitoring.report'], null=False)),
            ('check', models.ForeignKey(orm[u'monitoring.check'], null=False))
        ))
        db.create_unique(m2m_table_name, ['report_id', 'check_id'])

        # Adding M2M table for field groups on 'Report'
        m2m_table_name = db.shorten_name(u'monitoring_report_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('report', models.ForeignKey(orm[u'monitoring.report'], null=False)),
            ('group', models.ForeignKey(orm[u'monitoring.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['report_id', 'group_id'])


    def backwards(self, orm):
        # Deleting model 'Group'
        db.delete_table(u'monitoring_group')

        # Deleting model 'Check'
        db.delete_table(u'monitoring_check')

        # Deleting model 'CheckDailyReport'
        db.delete_table(u'monitoring_checkdailyreport')

        # Deleting model 'Problem'
        db.delete_table(u'monitoring_problem')

        # Deleting model 'Report'
        db.delete_table(u'monitoring_report')

        # Removing M2M table for field checks on 'Report'
        db.delete_table(db.shorten_name(u'monitoring_report_checks'))

        # Removing M2M table for field groups on 'Report'
        db.delete_table(db.shorten_name(u'monitoring_report_groups'))


    models = {
        u'monitoring.check': {
            'Meta': {'object_name': 'Check'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitoring.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintenance_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notification_addresses': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'monitoring.checkdailyreport': {
            'Meta': {'object_name': 'CheckDailyReport'},
            'check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitoring.Check']"}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintenance_mode': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status_critical': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status_disabled': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status_ok': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status_unknown': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status_warning': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'update_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'monitoring.group': {
            'Meta': {'object_name': 'Group'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notification_addresses': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'})
        },
        u'monitoring.problem': {
            'Meta': {'ordering': "('-start_time',)", 'object_name': 'Problem'},
            'acknowledged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitoring.Check']"}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'send_down_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'send_up_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'monitoring.report': {
            'Meta': {'object_name': 'Report'},
            'checks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['monitoring.Check']", 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['monitoring.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notification_addresses': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'schedule': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'})
        }
    }

    complete_apps = ['monitoring']