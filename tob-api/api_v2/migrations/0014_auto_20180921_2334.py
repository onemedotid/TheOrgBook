# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-21 23:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v2', '0013_auto_20180921_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='type',
            field=models.TextField(db_index=True, default='text'),
        ),
    ]
