import django
import os
import sys
from django.db.models import F
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rss_test.settings")
django.setup()

from django.contrib.auth.models import AnonymousUser, User
import django.contrib.postgres.search
from feed.models import *

#manager = Post.objects.all() # identify which manager you want
#for item in manager:
#    if(item.tag_set.count() >0):
#        print(item.description)

#tag_name = PostGroupName.objects.first()
#print(PostGroup.objects.values('post').filter(post__liked=False)[0]['post']) #tag_name)

#print('Tag iterator test')

#tags = PostGroupQuery(PostGroup.objects.all())
#for tag in tags[:2]:
#    print(tag)
name_liked = PostGroupName.objects.filter(name="#like")[0]

user = User.objects.filter(username="louise")[0]
#print(user[0])
for post in Post.objects.filter(liked=True):
    if PostGroup.objects.values('post').filter(post=post).count() == 0:
        PostGroup.objects.create(post=post,owner=user,name=name_liked).save()
    
#print(PostGroup.objects.values('post').values())
#print(Tag.objects.filter(post__liked=False)[:2])    
#print(tags[:2])
#print(Post.objects.tag_set.all())
#print(Post.objects.filter(=['trans']).all())

if sys.argv[1] == 'export':
    for feed in Post.objects.all():
        print(feed.title)
#        print(feed.metadata)
        print(feed.tags)
#        if 'tags' in feed.metadata:
#            print(feed.metadata['tags'])
#        if 'label' in feed.metadata:
#            print(feed.metadata['label'])
elif sys.argv[1] == 'import':
    for line in sys.stdin:
        feed = Feed(link=line,title="")
        feed.save()