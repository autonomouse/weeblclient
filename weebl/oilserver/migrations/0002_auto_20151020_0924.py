# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bug',
            old_name='bug_tracker_bug',
            new_name='bugtrackerbug',
        ),
        migrations.RenameField(
            model_name='build',
            old_name='build_status',
            new_name='buildstatus',
        ),
        migrations.RenameField(
            model_name='build',
            old_name='job_type',
            new_name='jobtype',
        ),
        migrations.RenameField(
            model_name='jenkins',
            old_name='service_status',
            new_name='servicestatus',
        ),
        migrations.RenameField(
            model_name='jenkins',
            old_name='service_status_updated_at',
            new_name='servicestatus_updated_at',
        ),
        migrations.RenameField(
            model_name='knownbugregex',
            old_name='target_file_globs',
            new_name='targetfileglobs',
        ),
        migrations.RenameField(
            model_name='pipeline',
            old_name='block_storage',
            new_name='blockstorage',
        ),
        migrations.RenameField(
            model_name='pipeline',
            old_name='build_executor',
            new_name='buildexecutor',
        ),
        migrations.RenameField(
            model_name='pipeline',
            old_name='image_storage',
            new_name='imagestorage',
        ),
        migrations.RenameField(
            model_name='pipeline',
            old_name='openstack_version',
            new_name='openstackversion',
        ),
        migrations.RenameField(
            model_name='pipeline',
            old_name='ubuntu_version',
            new_name='ubuntuversion',
        ),
        migrations.RenameField(
            model_name='targetfileglob',
            old_name='job_types',
            new_name='jobtypes',
        ),
    ]
