# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-08-20 15:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_highlights', '0047_auto_20180805_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scraperapikey',
            name='last_invalid_try',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 20, 15, 52, 43, 730057)),
        ),
    ]
