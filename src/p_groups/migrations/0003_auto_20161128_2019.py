# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 04:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('p_groups', '0002_auto_20161119_0358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_imp_rating',
            field=models.IntegerField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], max_length=1, null=True),
        ),
    ]