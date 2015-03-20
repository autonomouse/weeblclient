# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overview', '0002_auto_20150316_1809'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildConfiguration',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Charm',
            fields=[
                ('charm', models.CharField(serialize=False, primary_key=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('error_type', models.CharField(max_length=255)),
                ('error_hash', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hardware',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('hardware_type', models.CharField(max_length=255)),
                ('vendor', models.ForeignKey(to='overview.Pipeline')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('machine_name', models.CharField(max_length=255)),
                ('ip', models.CharField(max_length=255)),
                ('hardware', models.ForeignKey(to='overview.Hardware')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenStack',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('release_name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenStackComponents',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('component', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('distribution', models.CharField(max_length=255)),
                ('release_name', models.CharField(max_length=255)),
                ('release_version', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('port_number', models.IntegerField()),
                ('protocol', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Slave',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('slave', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('state', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TempestTestResult',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('skipped', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('time', models.CharField(max_length=255)),
                ('tempest_test', models.ForeignKey(to='overview.TempestTest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('unit_name', models.CharField(max_length=255)),
                ('unit_number', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='openstack',
            name='included_components',
            field=models.ManyToManyField(to='overview.OpenStackComponents'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='charm_used',
            field=models.ForeignKey(to='overview.Charm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='machine_used',
            field=models.ForeignKey(to='overview.Machine'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='openstack_used',
            field=models.ForeignKey(to='overview.OpenStack'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='operating_systems_used',
            field=models.ForeignKey(to='overview.OperatingSystem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='ports_used',
            field=models.ManyToManyField(to='overview.Port'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='reported_state',
            field=models.ForeignKey(to='overview.State'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='slave_used',
            field=models.ForeignKey(to='overview.Slave'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='buildconfiguration',
            name='units',
            field=models.ForeignKey(to='overview.Unit'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='tempesttest',
            name='message',
        ),
        migrations.RemoveField(
            model_name='tempesttest',
            name='skipped',
        ),
        migrations.RemoveField(
            model_name='tempesttest',
            name='time',
        ),
        migrations.AddField(
            model_name='build',
            name='analysed_by_crude_timestamp',
            field=models.DateTimeField(blank=True, default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='bootstrap_node_jenkins_used',
            field=models.ForeignKey(null=True, to='overview.Slave'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='bootstrap_node_machine_used',
            field=models.ForeignKey(null=True, to='overview.Machine'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='bootstrap_node_openstack_used',
            field=models.ForeignKey(null=True, to='overview.OpenStack'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='bootstrap_node_operating_systems_used',
            field=models.ForeignKey(null=True, to='overview.OperatingSystem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='bootstrap_node_reported_state',
            field=models.ForeignKey(null=True, to='overview.State'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='build_configuration',
            field=models.ManyToManyField(to='overview.BuildConfiguration'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='build',
            name='tempest_tests',
            field=models.ManyToManyField(to='overview.TempestTestResult'),
            preserve_default=True,
        ),
    ]
