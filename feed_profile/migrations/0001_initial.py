# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-11 21:29
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('content_type', models.CharField(default='text/x-markdown', max_length=64)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default='')),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=128), default=[], size=None)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]