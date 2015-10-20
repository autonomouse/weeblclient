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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Block Storage type.', unique=True, max_length=255, default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='UUID of this bug.', unique=True, max_length=36, default=utils.generate_uuid)),
                ('summary', models.CharField(help_text='Brief overview of bug.', unique=True, max_length=255, default=utils.generate_uuid)),
                ('description', models.TextField(help_text='Full description of bug.', null=True, blank=True, default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BugOccurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='UUID of this bug occurrence.', unique=True, max_length=36, default=utils.generate_uuid)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BugTrackerBug',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('bug_number', models.IntegerField(help_text='Designation of this bug (e.g. Launchpad bug number).', unique=True)),
                ('uuid', models.CharField(help_text='UUID of this bug.', unique=True, max_length=36, default=utils.generate_uuid)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='UUID of this build.', unique=True, max_length=36, default=utils.generate_uuid)),
                ('build_id', models.CharField(help_text='The build number or other identifier used by jenkins.', max_length=255)),
                ('artifact_location', models.URLField(help_text='URL where build artifacts can be obtainedIf archived, then         jenkins has been wiped and the build numbers reset, so this data is         no longer accessble via jenkins link', null=True, unique=True, default=None)),
                ('build_started_at', models.DateTimeField(help_text='DateTime the build was started.', null=True, blank=True, default=None)),
                ('build_finished_at', models.DateTimeField(help_text='DateTime the build finished.', null=True, blank=True, default=None)),
                ('build_analysed_at', models.DateTimeField(help_text='DateTime build analysed by weebl, or None if unanalysed.', null=True, blank=True, default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildExecutor',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='UUID of the jenkins build executor.', unique=True, max_length=36, default=utils.generate_uuid)),
                ('name', models.CharField(help_text='Name of the jenkins build executor.', max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The resulting state of the build.', unique=True, max_length=255, default='unknown')),
                ('description', models.TextField(help_text='Optional description for state.', null=True, blank=True, default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compute',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Compute type.', unique=True, max_length=255, default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Database type.', unique=True, max_length=255, default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='UUID of environment.', unique=True, max_length=36, default=utils.generate_uuid)),
                ('name', models.CharField(null=True, max_length=255, unique=True, help_text='Name of environment.', default=utils.generate_uuid, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Image Storage type.', unique=True, max_length=255, default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Jenkins',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='UUID of the jenkins instance.', unique=True, max_length=36, default=utils.generate_uuid)),
                ('external_access_url', models.URLField(help_text='A URL for external access to this server.', unique=True)),
                ('internal_access_url', models.URLField(null=True, unique=True, help_text='A URL used internally (e.g. behind a firewall) for access         to this server.', default=None, blank=True)),
                ('servicestatus_updated_at', models.DateTimeField(help_text='DateTime the service status was last updated.', auto_now_add=True, default=utils.time_now)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The type of job.', unique=True, max_length=255, default='pipeline_deploy')),
                ('description', models.TextField(help_text='Optional description of job type.', null=True, blank=True, default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KnownBugRegex',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='UUID of this pattern.', unique=True, max_length=36, default=utils.generate_uuid)),
                ('regex', models.TextField(help_text='The regular expression used to identify a bug occurrence.', unique=True)),
                ('bug', models.ForeignKey(to='oilserver.Bug', default=None, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenstackVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the version of the OpenStack system.', unique=True, max_length=255, default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(help_text='The pipeline ID (a UUID).', unique=True, max_length=36, default=utils.generate_uuid)),
                ('completed_at', models.DateTimeField(help_text='DateTime the pipeline was completed.', null=True, blank=True, default=None)),
                ('blockstorage', models.ForeignKey(to='oilserver.BlockStorage', default=None, null=True, blank=True)),
                ('buildexecutor', models.ForeignKey(to='oilserver.BuildExecutor')),
                ('compute', models.ForeignKey(to='oilserver.Compute', default=None, null=True, blank=True)),
                ('database', models.ForeignKey(to='oilserver.Database', default=None, null=True, blank=True)),
                ('imagestorage', models.ForeignKey(to='oilserver.ImageStorage', default=None, null=True, blank=True)),
                ('openstackversion', models.ForeignKey(to='oilserver.OpenstackVersion', default=None, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('name', models.CharField(help_text='Name of project.', max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SDN',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the software defined network.', unique=True, max_length=255, default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='Current state of the environment.', unique=True, max_length=255, default='unknown')),
                ('description', models.TextField(help_text='Optional description for status.', null=True, blank=True, default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TargetFileGlob',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('glob_pattern', models.TextField(help_text='Glob pattern used to match one or more target files.', unique=True)),
                ('jobtypes', models.ManyToManyField(null=True, to='oilserver.JobType', blank=True, default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UbuntuVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the version of the Ubuntu system.', unique=True, max_length=255, default='')),
                ('number', models.CharField(help_text='The numerical version of the Ubuntu system', unique=True, max_length=10, default='')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WeeblSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('check_in_unstable_threshold', models.IntegerField(help_text='The time (sec) taken for jenkins to check in, problem         suspected if over.', default=300)),
                ('check_in_down_threshold', models.IntegerField(help_text='The time (sec) taken for jenkins to check in, definate         problem if over.', default=1800)),
                ('low_build_queue_threshold', models.IntegerField(help_text='There are too few builds in queue when lower than this.', default=3)),
                ('overall_unstable_th', models.IntegerField(help_text='Overall success rate unstable thresholds.', default=65)),
                ('overall_down_th', models.IntegerField(help_text='Overall success rate down thresholds.', default=50)),
                ('down_colour', models.CharField(help_text='Highlight when warning.', max_length=25, default='red')),
                ('unstable_colour', models.CharField(help_text='Highlight when unstable.', max_length=25, default='orange')),
                ('up_colour', models.CharField(help_text='Highlight when no problems (up).', max_length=25, default='green')),
                ('weebl_documentation', models.URLField(help_text='URL to documentation.', blank=True, default=None)),
                ('site', models.OneToOneField(to='sites.Site', help_text='To make sure there is only ever one instance per website.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='sdn',
            field=models.ForeignKey(to='oilserver.SDN', default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pipeline',
            name='ubuntuversion',
            field=models.ForeignKey(to='oilserver.UbuntuVersion', default=None, null=True, blank=True),
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
            field=models.ForeignKey(to='oilserver.Project', default=None, null=True, blank=True),
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
            field=models.OneToOneField(to='oilserver.BugTrackerBug', help_text='Bug tracker bug associated with this bug.', null=True, default=None, blank=True),
            preserve_default=True,
        ),
    ]
