# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-20 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tag_description',
            field=models.TextField(max_length=400),
        ),
    ]
