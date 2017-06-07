# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 23:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0008_auto_20161124_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='master',
            name='first_met',
            field=models.DateField(default=datetime.date(2016, 11, 24)),
        ),
        migrations.AlterField(
            model_name='master',
            name='met_where',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]