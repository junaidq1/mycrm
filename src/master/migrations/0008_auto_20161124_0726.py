# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 07:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0007_master_target_contact_cycle_individual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='master',
            name='tag1',
            field=models.ManyToManyField(blank=True, to='tags.Tag'),
        ),
    ]
