# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 03:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('p_groups', '0001_initial'),
        ('master', '0002_auto_20161119_0312'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='primary_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='p_groups.Group'),
            preserve_default=False,
        ),
    ]
