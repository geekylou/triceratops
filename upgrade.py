import django
import os
import sys
from django.db.models import F
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rss_test.settings")
django.setup()

from django.contrib.auth.models import AnonymousUser, User
import django.contrib.postgres.search
from feed.models import *

# Upgrade from global pinned values to per users pinned valued.

name_liked = PostGroupName.objects.filter(name="#like")
if name_liked.count() == 0:
    name_liked = PostGroupName.objects.create(name="#like")
else:
    name_liked = name_liked[0]
user = User.objects.filter(username="louise")[0]

for post in Post.objects.filter(liked=True):
    if PostGroup.objects.values('post').filter(post=post).count() == 0:
        PostGroup.objects.create(post=post,owner=user,name=name_liked).save()
    
