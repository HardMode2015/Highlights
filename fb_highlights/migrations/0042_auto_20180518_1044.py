# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-18 10:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fb_highlights', '0041_latesthighlight_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='user',
            name='image_url',
        ),
    ]
