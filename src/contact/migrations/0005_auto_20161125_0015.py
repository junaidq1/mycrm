# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-25 00:15
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0004_auto_20161124_2355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact_log',
            name='contact_date',
            field=models.DateField(default=datetime.date(2016, 11, 25)),
        ),
    ]