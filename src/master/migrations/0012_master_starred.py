# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-25 07:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0011_auto_20161125_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='starred',
            field=models.BooleanField(default=False),
        ),
    ]
