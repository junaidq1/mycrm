# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 04:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0014_auto_20161128_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='master',
            name='ind_imp_rating',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='master.Importance'),
        ),
    ]
