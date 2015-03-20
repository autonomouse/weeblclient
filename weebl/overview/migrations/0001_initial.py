# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('bug_id', models.IntegerField(primary_key=True, serialize=False)),
                ('filed_status', models.CharField(max_length=255)),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('assignee', models.CharField(max_length=255)),
                ('date_last_message', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_last_updated', models.DateTimeField(default=None, blank=True, null=True)),
                ('bug_heat', models.IntegerField()),
                ('iso_date_created', models.CharField(max_length=255)),
                ('last_update', models.IntegerField()),
                ('latest_patch_uploaded', models.IntegerField()),
                ('number_affected', models.IntegerField()),
                ('number_of_duplicates', models.IntegerField()),
                ('number_of_messages', models.IntegerField()),
                ('number_subscribed', models.IntegerField()),
                ('series_name', models.CharField(max_length=255)),
                ('series_version', models.CharField(max_length=255)),
                ('bug_target_name', models.CharField(max_length=255)),
                ('date_assigned', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_closed', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_confirmed', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_created', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_fix_committed', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_fix_released', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_in_progress', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_incomplete', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_left_closed', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_left_new', models.DateTimeField(default=None, blank=True, null=True)),
                ('date_triaged', models.DateTimeField(default=None, blank=True, null=True)),
                ('importance', models.CharField(max_length=255)),
                ('is_complete', models.BooleanField(default=False)),
                ('milestone_found', models.CharField(max_length=255)),
                ('milestone_target', models.CharField(max_length=255)),
                ('owner', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('web_link', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BugTracker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('bug_tracker_name', models.CharField(max_length=255)),
                ('bug_tracker_link', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('build_number', models.IntegerField()),
                ('job', models.CharField(max_length=255)),
                ('jenkins_link', models.URLField()),
                ('archived', models.BooleanField(default=False)),
                ('build_start_timestamp', models.DateTimeField(default=None, blank=True, null=True)),
                ('build_complete_timestamp', models.DateTimeField(default=None, blank=True, null=True)),
                ('still_active', models.BooleanField(default=True)),
                ('build_failed', models.BooleanField(default=False)),
                ('tempest_testsuite_name', models.CharField(max_length=255)),
                ('tempest_total_tests', models.IntegerField()),
                ('tempest_total_errors', models.IntegerField()),
                ('tempest_total_failures', models.IntegerField()),
                ('tempest_total_skip', models.IntegerField()),
                ('success_rate', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('environment', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HighLevelCategory',
            fields=[
                ('category', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('job', models.CharField(max_length=255)),
                ('warning_threshold', models.IntegerField()),
                ('critical_threshold', models.IntegerField()),
                ('environment', models.ForeignKey(to='overview.Environment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MaintenanceEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('event', models.CharField(max_length=255)),
                ('summary', models.TextField()),
                ('timestamp', models.DateTimeField(default=None, blank=True, null=True)),
                ('details', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('pipeline_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('test_catalog_link', models.URLField()),
                ('jobs', models.ManyToManyField(to='overview.Job')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Regexp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('target_filename', models.CharField(max_length=255)),
                ('regexp', models.TextField()),
                ('bug_id', models.ForeignKey(to='overview.Bug')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('tag', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TempestTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('test_classname', models.CharField(max_length=255)),
                ('test_name', models.CharField(max_length=255)),
                ('skipped', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('time', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vendors',
            fields=[
                ('vendor', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('joined_OIL', models.DateTimeField(default=None, blank=True, null=True)),
                ('left_OIL', models.DateTimeField(default=None, blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='highlevelcategory',
            name='tags',
            field=models.ManyToManyField(to='overview.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='maintenance_events',
            field=models.ManyToManyField(to='overview.MaintenanceEvent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='environment',
            field=models.ForeignKey(to='overview.Environment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='pipeline_id',
            field=models.ForeignKey(to='overview.Pipeline'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='tempest_tests',
            field=models.ManyToManyField(to='overview.TempestTest'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bug',
            name='affected_pipelines',
            field=models.ManyToManyField(to='overview.Pipeline'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bug',
            name='categories',
            field=models.ManyToManyField(to='overview.HighLevelCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bug',
            name='environments',
            field=models.ManyToManyField(to='overview.Environment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bug',
            name='jobs',
            field=models.ManyToManyField(to='overview.Job'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bug',
            name='tags',
            field=models.ManyToManyField(to='overview.Tag'),
            preserve_default=True,
        ),
    ]
