# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-04-29 17:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_highlights', '0033_latesthighlight_goal_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='see_result',
            field=models.BooleanField(default=True),
        ),
    ]
