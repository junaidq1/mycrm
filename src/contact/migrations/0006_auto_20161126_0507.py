# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 05:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0005_auto_20161125_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact_log',
            name='contact_date',
            field=models.DateField(default=datetime.date(2016, 11, 26)),
        ),
    ]
