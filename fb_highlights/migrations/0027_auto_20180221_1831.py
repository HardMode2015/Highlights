# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-21 18:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_highlights', '0026_auto_20180221_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='latesthighlight',
            name='video_duration',
            field=models.IntegerField(default=0),
        ),
    ]