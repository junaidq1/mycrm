# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 07:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0006_auto_20161124_0721'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='target_contact_cycle_individual',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]