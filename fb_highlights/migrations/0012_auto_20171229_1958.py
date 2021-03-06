# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-29 19:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb_highlights', '0011_auto_20171226_2334'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='latesthighlight',
            name='id',
        ),
        migrations.AddField(
            model_name='latesthighlight',
            name='category',
            field=models.CharField(default='no category', max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='latesthighlight',
            name='img_link',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='latesthighlight',
            name='score1',
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='latesthighlight',
            name='score2',
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='latesthighlight',
            name='view_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='latesthighlight',
            name='link',
            field=models.TextField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='latesthighlight',
            name='time_since_added',
            field=models.CharField(max_length=120),
        ),
    ]
