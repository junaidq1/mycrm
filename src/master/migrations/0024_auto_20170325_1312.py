# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-25 20:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0023_master_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='master',
            name='city',
            field=models.CharField(default='unknown', max_length=120),
        ),
    ]
