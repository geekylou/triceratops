from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.search import SearchVectorField,SearchVector
from django.contrib.postgres.fields import JSONField,ArrayField

import markdown2
import rss_test.settings

def update_indexes():
    Post.objects.update(search_vector_description=SearchVector('title'))
    Post.objects.update(search_vector_description=SearchVector('description'))

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
    feed = models.ForeignKey(
    Feed,
    on_delete=models.CASCADE,
    )
    title = models.TextField(max_length=1024,null=True,blank=True)
    published = models.DateTimeField(null=True,blank=True)
    link = models.CharField(primary_key=True,max_length=255)
    description = models.TextField(blank=True)
    liked       = models.BooleanField(default=False)
    content_type = models.CharField(default="text/html",max_length=64)
    metadata = JSONField(default="")
    tags = ArrayField(models.CharField(max_length=128, blank=True),default=[])
    
    search_vector_description = SearchVectorField(description)
    
    def html(self):
        if self.content_type=='text/x-markdown':
            return markdown2.markdown(self.description,extras=['nofollow','fenced-code-blocks'])
        elif self.content_type=='text/html':
            return self.description
        return "<b>Error: Cannot process data!<b>";
    
    def get_title(self):
        if self.title=="":
            return self.description.split('\n')[0]
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

@python_2_unicode_compatible
class TagName(models.Model):
    name = models.CharField(primary_key=True,max_length=255)
    
@python_2_unicode_compatible
class Tag(models.Model):
    post = models.ForeignKey(
    Post,
    on_delete=models.CASCADE,
    )
    name = models.ForeignKey(
    TagName,
    on_delete=models.CASCADE,
    )
