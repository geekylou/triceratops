
"""rss_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import feed.views

urlpatterns = [
    url(r'^rss/$', feed.views.index, name='index'),
    url(r'^rss/action$', feed.views.action, name='action'),
    url(r'^rss/upload$', feed.views.upload, name='upload'),
    url(r'^rss/feeds$', feed.views.feeds, name='feeds'),
    url(r'^rss/post/(?P<url>[\w\-]+)$', feed.views.post, name='post'),
    url(r'^rss/feed/(?P<url>[\w\-]+)$', feed.views.feed, name='feed'),
    url(r'^rss/tag/(?P<tag_name>.+)$', feed.views.tag, name='tag'),
    url(r'^rss/base$', feed.views.base, name='base'),
    url(r'^rss/admin/', admin.site.urls),
]
admin.site.site_url = '/rss'