from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Feed, Post, PostGroup, PostGroupName

admin.site.register(Feed)
admin.site.register(Post)
admin.site.register(PostGroupName)
admin.site.register(PostGroup)