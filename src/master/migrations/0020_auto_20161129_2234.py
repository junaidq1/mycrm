# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 06:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0019_auto_20161128_2113'),
    ]

    operations = [
        migrations.CreateModel(
            name='Importance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importance_descrip', models.CharField(max_length=30)),
                ('importance_ranking', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='master',
            name='first_met',
            field=models.DateField(blank=True, default=datetime.date(2016, 11, 29), null=True),
        ),
    ]
