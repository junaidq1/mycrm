# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-20 17:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact_log',
            name='next_contact_date',
        ),
        migrations.AlterField(
            model_name='contact_log',
            name='contact_date',
            field=models.DateField(default=datetime.date(2016, 11, 20)),
        ),
    ]
