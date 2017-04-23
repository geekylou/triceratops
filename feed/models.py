from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.search import SearchVectorField,SearchVector
from django.contrib.postgres.fields import JSONField,ArrayField
from django.conf import settings

import markdown2
import triceratops.settings
import bleach

def update_indexes():
    Post.objects.update(search_vector_description=SearchVector('title'))
    Post.objects.update(search_vector_description=SearchVector('description'))

BLEACH_ATTR = bleach.ALLOWED_ATTRIBUTES.copy()
BLEACH_ATTR['img'] = ['src']
BLEACH_ATTR['time'] = ['*']

def filter(data):
    return bleach.clean(
        data,
        tags=bleach.ALLOWED_TAGS+['img','br','p','h1','h2','h3','h4','h5','h6','span','time','figure','sup'],
        attributes=BLEACH_ATTR)
    
# Create your models here.

@python_2_unicode_compatible
class Feed(models.Model):
    title = models.TextField(max_length=1024,null=True,blank=True)
    updated = models.DateTimeField(null=True,blank=True)
    link = models.CharField(max_length=255)
    url = models.CharField(max_length=255,blank=True) # link to the web site stored in the rss feed
    description = models.TextField(blank=True)
    description_type = models.CharField(default="text/plain",max_length=64)
    public      = models.BooleanField(default=False)
    enabled     = models.BooleanField(default=True)
    def __str__(self):
        if self.title != "":
            return self.title
        else:
            return self.link

    def get_url(self):
        if self.link.startswith('local://'):
            return rss_test.settings.BASE_URL+'feed/'+self.link[8:]
        else:
            return self.link
@python_2_unicode_compatible
class Post(models.Model):
    class Meta:
        ordering = ['-published']
    feed = models.ForeignKey(
    Feed,
    on_delete=models.CASCADE,
    )
    title = models.TextField(max_length=1024,null=True,blank=True)
    published = models.DateTimeField(null=True,blank=True)
    link = models.CharField(primary_key=True,max_length=255)
    description = models.TextField(blank=True)
    
    #liked = models.BooleanField(default=False)
    content_type = models.CharField(default="text/html",max_length=64)
    metadata = JSONField(default="")
    tags = ArrayField(models.CharField(max_length=128, blank=True),default=[])
    
    search_vector_description = SearchVectorField(description)
    
    def html(self):
        if self.content_type=='text/x-markdown':
            return markdown2.markdown(self.description,extras=['nofollow','fenced-code-blocks'])
        elif self.content_type=='text/html':
            return filter(self.description)
        return "<b>Error: Cannot process data!<b>";
    
    def get_title(self):
        if self.title=="":
            title = "<no-title>"
            for line in self.description.split('\n'):
                if line != "":
                    title = line
            return title
        else:
            return self.title
            
    def get_url(self):
        if self.link.startswith('local://'):
            return rss_test.settings.BASE_URL+'post/'+self.link[8:]
        else:
            return self.link
            
    def is_editable(self):
        return (self.link.startswith('local://') and self.content_type=='text/x-markdown')
    
    def _is_editable(self,user):
        return is_editable(self)
        
    def safe_delete(self,user):
        if self.link.startswith('local://'):
            self.delete();
            return True
        return False

    def is_liked(self):
        return self.liked
    
    def __str__(self):
        if self.title != "":
            ret = self.title
        else:
            ret = self.link
        return ret
    def dict(self):
        return {
            'description': self.description,
            'description_type': self.content_type,
            'title': self.title,
        }

class FeedQuery:
    def __init__(self,queryset,user,liked_query=None):
        self.queryset = queryset
        self.user = user
        self.liked_queryset = liked_query
        
    def liked(self):
        if self.liked_queryset == None and self.user.is_authenticated:
            self.liked_queryset = PostGroupQuery(PostGroup.objects.filter(owner=self.user).filter(name="#like"))
        return self.liked_queryset

    def __getitem__(self, k):
        return FeedQuery(self.queryset[k],self.user)
        
    def __len__(self):
        return len(self.queryset)
    
    def __iter__(self):
        if self.user.is_authenticated:
            liked_posts = self.liked().queryset.values("post").values()
            liked_set = frozenset(o['post_id'] for o in liked_posts)
        else:
            liked_set = frozenset([])
            
        for item in self.queryset:
            item.liked=item.pk in liked_set
            yield item
            
    def filter(self,**kwargs):
        liked_queryset = None
        if self.liked() != None:
            liked_queryset = self.liked().filter(**kwargs)
        return FeedQuery(self.queryset.filter(**kwargs),self.user,liked_query=liked_queryset)
    
    def first(self):
        return self.__iter__().__next__()
    
    def all(self):
        return list(self)
    
    def count(self):
        return self.queryset.count()

class PostGroupQuery:
    def __init__(self,queryset):
        self.queryset = queryset
        
    def __getitem__(self, k):
        return PostGroupQuery(self.queryset[k])
        
    def __len__(self):
        return len(self.queryset)
    
    def __iter__(self):
        for item in self.queryset:
            item.post.liked=True
            yield item.post
            
    def filter(self,**kwargs):
        args={}
        for key, value in kwargs.items():
            args["post__"+key]=value
        return PostGroupQuery(self.queryset.filter(**args))
    
    def all(self):
        return list(self)
    
    def first(self):
        return  self.__iter__().__next__()
    
    def count(self):
        return self.queryset.count()
    
    def order_by(self,arg):
        if arg[0] == "-":
            sign="-"
            arg=arg[1:]
        else:
            sign=""
        return PostGroupQuery(self.queryset.order_by(sign+"post__"+arg))
            
@python_2_unicode_compatible
class PostGroupName(models.Model):
    name = models.CharField(primary_key=True,max_length=255)

    def __str__(self):
        return self.name
    
@python_2_unicode_compatible
class PostGroup(models.Model):
    post = models.ForeignKey(
    Post,
    on_delete=models.CASCADE,
    )
    name = models.ForeignKey(
    PostGroupName,
    on_delete=models.CASCADE,
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
      return str(self.name)+":"+str(self.post)