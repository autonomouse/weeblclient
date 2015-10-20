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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The name of the Block Storage type.', default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of this bug.', default=utils.generate_uuid)),
                ('summary', models.CharField(unique=True, max_length=255, help_text='Brief overview of bug.', default=utils.generate_uuid)),
                ('description', models.TextField(blank=True, null=True, help_text='Full description of bug.', default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BugOccurrence',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of this bug occurrence.', default=utils.generate_uuid)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BugTrackerBug',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('bug_number', models.IntegerField(unique=True, help_text='Designation of this bug (e.g. Launchpad bug number).')),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of this bug.', default=utils.generate_uuid)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of this build.', default=utils.generate_uuid)),
                ('build_id', models.CharField(max_length=255, help_text='The build number or other identifier used by jenkins.')),
                ('artifact_location', models.URLField(unique=True, null=True, help_text='URL where build artifacts can be obtainedIf archived, then         jenkins has been wiped and the build numbers reset, so this data is         no longer accessble via jenkins link', default=None)),
                ('build_started_at', models.DateTimeField(blank=True, null=True, help_text='DateTime the build was started.', default=None)),
                ('build_finished_at', models.DateTimeField(blank=True, null=True, help_text='DateTime the build finished.', default=None)),
                ('build_analysed_at', models.DateTimeField(blank=True, null=True, help_text='DateTime build analysed by weebl, or None if unanalysed.', default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildExecutor',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of the jenkins build executor.', default=utils.generate_uuid)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The resulting state of the build.', default='unknown')),
                ('description', models.TextField(blank=True, null=True, help_text='Optional description for state.', default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compute',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The name of the Compute type.', default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The name of the Database type.', default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of environment.', default=utils.generate_uuid)),
                ('name', models.CharField(unique=True, blank=True, max_length=255, default=utils.generate_uuid, null=True, help_text='Name of environment.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageStorage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The name of the Image Storage type.', default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Jenkins',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of the jenkins instance.', default=utils.generate_uuid)),
                ('external_access_url', models.URLField(unique=True, help_text='A URL for external access to this server.')),
                ('internal_access_url', models.URLField(unique=True, blank=True, default=None, null=True, help_text='A URL used internally (e.g. behind a firewall) for access         to this server.')),
                ('service_status_updated_at', models.DateTimeField(help_text='DateTime the service status was last updated.', auto_now_add=True, default=utils.time_now)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The type of job.', default='pipeline_deploy')),
                ('description', models.TextField(blank=True, null=True, help_text='Optional description of job type.', default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KnownBugRegex',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='UUID of this pattern.', default=utils.generate_uuid)),
                ('regex', models.TextField(unique=True, help_text='The regular expression used to identify a bug occurrence.')),
                ('bug', models.ForeignKey(default=None, null=True, blank=True, to='oilserver.Bug')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenstackVersion',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The name of the version of the OpenStack system.', default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('uuid', models.CharField(unique=True, max_length=36, help_text='The pipeline ID (a UUID).', default=utils.generate_uuid)),
                ('completed_at', models.DateTimeField(blank=True, null=True, help_text='DateTime the pipeline was completed.', default=None)),
                ('block_storage', models.ForeignKey(default=None, null=True, blank=True, to='oilserver.BlockStorage')),
                ('build_executor', models.ForeignKey(to='oilserver.BuildExecutor')),
                ('compute', models.ForeignKey(default=None, null=True, blank=True, to='oilserver.Compute')),
                ('database', models.ForeignKey(default=None, null=True, blank=True, to='oilserver.Database')),
                ('image_storage', models.ForeignKey(default=None, null=True, blank=True, to='oilserver.ImageStorage')),
                ('openstack_version', models.ForeignKey(default=None, null=True, blank=True, to='oilserver.OpenstackVersion')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('name', models.CharField(unique=True, help_text='Name of project.', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SDN',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The name of the software defined network.', default='unknown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='Current state of the environment.', default='unknown')),
                ('description', models.TextField(blank=True, null=True, help_text='Optional description for status.', default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TargetFileGlob',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(blank=True, null=True, help_text='DateTime this model instance was created.', default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', auto_now_add=True, default=utils.time_now)),
                ('glob_pattern', models.TextField(unique=True, help_text='Glob pattern used to match one or more target files.')),
                ('job_types', models.ManyToManyField(to='oilserver.JobType', null=True, blank=True, default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UbuntuVersion',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The name of the version of the Ubuntu system.', default='')),
                ('number', models.CharField(unique=True, max_length=10, help_text='The numerical version of the Ubuntu system', default='')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WeeblSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('check_in_unstable_threshold', models.IntegerField(help_text='The time (sec) taken for jenkins to check in, problem         suspected if over.', default=300)),
                ('check_in_down_threshold', models.IntegerField(help_text='The time (sec) taken for jenkins to check in, definate         problem if over.', default=1800)),
                ('low_build_queue_threshold', models.IntegerField(help_text='There are too few builds in queue when lower than this.', default=3)),
                ('overall_unstable_th', models.IntegerField(help_text='Overall success rate unstable thresholds.', default=65)),
                ('overall_down_th', models.IntegerField(help_text='Overall success rate down thresholds.', default=50)),
                ('down_colour', models.CharField(max_length=25, help_text='Highlight when warning.', default='red')),
                ('unstable_colour', models.CharField(max_length=25, help_text='Highlight when unstable.', default='orange')),
                ('up_colour', models.CharField(max_length=25, help_text='Highlight when no problems (up).', default='green')),
                ('weebl_documentation', models.URLField(blank=True, help_text='URL to documentation.', default=None)),
                ('site', models.OneToOneField(help_text='To make sure there is only ever one instance per website.', to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='sdn',
            field=models.ForeignKey(default=None, null=True, blank=True, to='oilserver.SDN'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pipeline',
            name='ubuntu_version',
            field=models.ForeignKey(default=None, null=True, blank=True, to='oilserver.UbuntuVersion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='knownbugregex',
            name='target_file_globs',
            field=models.ManyToManyField(to='oilserver.TargetFileGlob'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jenkins',
            name='service_status',
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
            name='build_status',
            field=models.ForeignKey(to='oilserver.BuildStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='job_type',
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
            field=models.ForeignKey(default=None, null=True, blank=True, to='oilserver.Project'),
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
            name='bug_tracker_bug',
            field=models.OneToOneField(blank=True, default=None, null=True, help_text='Bug tracker bug associated with this bug.', to='oilserver.BugTrackerBug'),
            preserve_default=True,
        ),
    ]
