from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Feed, Post, Tag, TagName

admin.site.register(Feed)
admin.site.register(Post)
admin.site.register(TagName)
admin.site.register(Tag)