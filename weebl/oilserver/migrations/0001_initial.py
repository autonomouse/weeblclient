# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeblSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('check_in_unstable_threshold', models.IntegerField(help_text='The time (sec) taken for jenkins to check in, problem         suspected if over.', default=300)),
                ('check_in_down_threshold', models.IntegerField(help_text='The time (sec) taken for jenkins to check in, definate         problem if over.', default=1800)),
                ('low_build_queue_threshold', models.IntegerField(help_text='There are too few builds in queue when lower than this.', default=3)),
                ('overall_unstable_th', models.IntegerField(help_text='Overall success rate unstable thresholds.', default=65)),
                ('overall_down_th', models.IntegerField(help_text='Overall success rate down thresholds.', default=50)),
                ('down_colour', models.CharField(help_text='Highlight when warning.', default='red', max_length=25)),
                ('unstable_colour', models.CharField(help_text='Highlight when unstable.', default='orange', max_length=25)),
                ('up_colour', models.CharField(help_text='Highlight when no problems (up).', default='green', max_length=25)),
                ('weebl_documentation', models.URLField(help_text='URL to documentation.', default=None, blank=True)),
                ('site', models.OneToOneField(help_text='To make sure there is only ever one instance per website.', to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
