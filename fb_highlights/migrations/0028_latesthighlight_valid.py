# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-25 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_highlights', '0027_auto_20180221_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='latesthighlight',
            name='valid',
            field=models.BooleanField(default=True),
        ),
    ]
