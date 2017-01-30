from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

@python_2_unicode_compatible
class Feed(models.Model):
    title = models.CharField(max_length=1024,null=True,blank=True)
    updated = models.DateTimeField(null=True,blank=True)
    link = models.CharField(max_length=1024)
    url = models.CharField(max_length=1024,blank=True) # link to the web site stored in the rss feed
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
    title = models.CharField(max_length=1024,null=True,blank=True)
    published = models.DateTimeField(null=True,blank=True)
    link = models.CharField(primary_key=True,max_length=1024)
    description = models.TextField(blank=True)
    def __str__(self):
        if self.title != "":
            ret = self.title
        else:
            ret = self.link
        return ret   