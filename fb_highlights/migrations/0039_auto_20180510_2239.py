# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-10 22:39
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb_highlights', '0038_auto_20180507_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='latesthighlight',
            name='goal_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
    ]