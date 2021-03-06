# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 03:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('master', '0003_master_primary_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_date', models.DateField(default=datetime.date(2016, 11, 19))),
                ('contact_type', models.CharField(choices=[('in_person', 'in_person'), ('email', 'email'), ('text', 'text'), ('phone', 'phone'), ('socialmedia', 'socialmedia'), ('other', 'other')], max_length=12)),
                ('contact_notes', models.TextField(max_length=500, null=True)),
                ('next_contact_date', models.DateField(blank=True, null=True)),
                ('contact_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.Master')),
            ],
        ),
    ]
