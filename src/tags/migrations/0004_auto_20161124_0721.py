# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0003_auto_20161120_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tag_description',
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
    ]
