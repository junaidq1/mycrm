# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-07 05:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('p_groups', '0008_auto_20161128_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='target_contact_cycle_weeks',
            field=models.IntegerField(default=2003),
            preserve_default=False,
        ),
    ]