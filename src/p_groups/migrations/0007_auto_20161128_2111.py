# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 05:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('p_groups', '0006_auto_20161128_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_imp_rating',
            field=models.CharField(choices=[('extremely important', 'extremely important'), ('important', 'important'), ('medium importance', 'medium importance'), ('low importance', 'low importance')], max_length=24),
        ),
    ]