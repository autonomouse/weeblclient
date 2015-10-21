# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockStorage',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='The name of the Block Storage type.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of this bug.')),
                ('summary', models.CharField(unique=True, default=utils.generate_uuid, max_length=255, help_text='Brief overview of bug.')),
                ('description', models.TextField(blank=True, default=None, help_text='Full description of bug.', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BugOccurrence',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of this bug occurrence.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BugTrackerBug',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('bug_number', models.IntegerField(unique=True, help_text='Designation of this bug (e.g. Launchpad bug number).')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of this bug.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of this build.')),
                ('build_id', models.CharField(max_length=255, help_text='The build number or other identifier used by jenkins.')),
                ('artifact_location', models.URLField(unique=True, null=True, default=None, help_text='URL where build artifacts can be obtainedIf archived, then         jenkins has been wiped and the build numbers reset, so this data is         no longer accessble via jenkins link')),
                ('build_started_at', models.DateTimeField(blank=True, default=None, help_text='DateTime the build was started.', null=True)),
                ('build_finished_at', models.DateTimeField(blank=True, default=None, help_text='DateTime the build finished.', null=True)),
                ('build_analysed_at', models.DateTimeField(blank=True, default=None, help_text='DateTime build analysed by weebl, or None if unanalysed.', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildExecutor',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of the jenkins build executor.')),
                ('name', models.CharField(max_length=255, help_text='Name of the jenkins build executor.')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='The resulting state of the build.')),
                ('description', models.TextField(blank=True, default=None, help_text='Optional description for state.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compute',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='The name of the Compute type.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='The name of the Database type.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of environment.')),
                ('name', models.CharField(unique=True, default=utils.generate_uuid, max_length=255, blank=True, help_text='Name of environment.', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageStorage',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='The name of the Image Storage type.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Jenkins',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of the jenkins instance.')),
                ('external_access_url', models.URLField(unique=True, help_text='A URL for external access to this server.')),
                ('internal_access_url', models.URLField(unique=True, default=None, blank=True, help_text='A URL used internally (e.g. behind a firewall) for access         to this server.', null=True)),
                ('servicestatus_updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime the service status was last updated.')),
                ('environment', models.OneToOneField(to='oilserver.Environment')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='pipeline_deploy', max_length=255, help_text='The type of job.')),
                ('description', models.TextField(blank=True, default=None, help_text='Optional description of job type.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KnownBugRegex',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='UUID of this pattern.')),
                ('regex', models.TextField(unique=True, help_text='The regular expression used to identify a bug occurrence.')),
                ('bug', models.ForeignKey(to='oilserver.Bug', default=None, blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenstackVersion',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='The name of the version of the OpenStack system.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(unique=True, default=utils.generate_uuid, max_length=36, help_text='The pipeline ID (a UUID).')),
                ('completed_at', models.DateTimeField(blank=True, default=None, help_text='DateTime the pipeline was completed.', null=True)),
                ('blockstorage', models.ForeignKey(to='oilserver.BlockStorage', default=None, blank=True, null=True)),
                ('buildexecutor', models.ForeignKey(to='oilserver.BuildExecutor')),
                ('compute', models.ForeignKey(to='oilserver.Compute', default=None, blank=True, null=True)),
                ('database', models.ForeignKey(to='oilserver.Database', default=None, blank=True, null=True)),
                ('imagestorage', models.ForeignKey(to='oilserver.ImageStorage', default=None, blank=True, null=True)),
                ('openstackversion', models.ForeignKey(to='oilserver.OpenstackVersion', default=None, blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('name', models.CharField(unique=True, max_length=255, help_text='Name of project.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SDN',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='The name of the software defined network.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='unknown', max_length=255, help_text='Current state of the environment.')),
                ('description', models.TextField(blank=True, default=None, help_text='Optional description for status.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TargetFileGlob',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('glob_pattern', models.TextField(unique=True, help_text='Glob pattern used to match one or more target files.')),
                ('jobtypes', models.ManyToManyField(blank=True, to='oilserver.JobType', default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UbuntuVersion',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, default='', max_length=255, help_text='The name of the version of the Ubuntu system.')),
                ('number', models.CharField(unique=True, default='', max_length=10, help_text='The numerical version of the Ubuntu system')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WeeblSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('check_in_unstable_threshold', models.IntegerField(default=300, help_text='The time (sec) taken for jenkins to check in, problem         suspected if over.')),
                ('check_in_down_threshold', models.IntegerField(default=1800, help_text='The time (sec) taken for jenkins to check in, definate         problem if over.')),
                ('low_build_queue_threshold', models.IntegerField(default=3, help_text='There are too few builds in queue when lower than this.')),
                ('overall_unstable_th', models.IntegerField(default=65, help_text='Overall success rate unstable thresholds.')),
                ('overall_down_th', models.IntegerField(default=50, help_text='Overall success rate down thresholds.')),
                ('down_colour', models.CharField(default='red', max_length=25, help_text='Highlight when warning.')),
                ('unstable_colour', models.CharField(default='orange', max_length=25, help_text='Highlight when unstable.')),
                ('up_colour', models.CharField(default='green', max_length=25, help_text='Highlight when no problems (up).')),
                ('weebl_documentation', models.URLField(blank=True, default=None, help_text='URL to documentation.')),
                ('site', models.OneToOneField(to='sites.Site', help_text='To make sure there is only ever one instance per website.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='sdn',
            field=models.ForeignKey(to='oilserver.SDN', default=None, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pipeline',
            name='ubuntuversion',
            field=models.ForeignKey(to='oilserver.UbuntuVersion', default=None, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='knownbugregex',
            name='targetfileglobs',
            field=models.ManyToManyField(to='oilserver.TargetFileGlob'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jenkins',
            name='servicestatus',
            field=models.ForeignKey(to='oilserver.ServiceStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildexecutor',
            name='jenkins',
            field=models.ForeignKey(to='oilserver.Jenkins'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='buildexecutor',
            unique_together=set([('name', 'jenkins')]),
        ),
        migrations.AddField(
            model_name='build',
            name='buildstatus',
            field=models.ForeignKey(to='oilserver.BuildStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='jobtype',
            field=models.ForeignKey(to='oilserver.JobType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='pipeline',
            field=models.ForeignKey(to='oilserver.Pipeline'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bugtrackerbug',
            name='project',
            field=models.ForeignKey(to='oilserver.Project', default=None, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bugoccurrence',
            name='build',
            field=models.ForeignKey(to='oilserver.Build'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bugoccurrence',
            name='regex',
            field=models.ForeignKey(to='oilserver.KnownBugRegex'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='bugoccurrence',
            unique_together=set([('build', 'regex')]),
        ),
        migrations.AddField(
            model_name='bug',
            name='bugtrackerbug',
            field=models.OneToOneField(to='oilserver.BugTrackerBug', default=None, blank=True, help_text='Bug tracker bug associated with this bug.', null=True),
            preserve_default=True,
        ),
    ]
