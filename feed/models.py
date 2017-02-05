from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

@python_2_unicode_compatible
class Feed(models.Model):
    title = models.TextField(max_length=1024,null=True,blank=True)
    updated = models.DateTimeField(null=True,blank=True)
    link = models.CharField(max_length=255)
    url = models.CharField(max_length=255,blank=True) # link to the web site stored in the rss feed
    description = models.TextField(blank=True)
    public      = models.BooleanField(default=False)
    enabled     = models.BooleanField(default=True)
    def __str__(self):
        if self.title != "":
            return self.title
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
    def __str__(self):
        if self.title != "":
            ret = self.title
        else:
            ret = self.link
        return ret

@python_2_unicode_compatible
class TagName(models.Model):
    name = models.CharField(primary_key=True,max_length=255)
    
@python_2_unicode_compatible
class Tag(models.Model):
    post = models.ForeignKey(
    Post,
    on_delete=models.CASCADE,
    )
    feed = models.ForeignKey(
    Feed,
    on_delete=models.CASCADE,
    )
    name = models.ForeignKey(
    TagName,
    on_delete=models.CASCADE,
    )
