import feedparser,os
import django
import sys
import html
import bleach
import traceback
import sys

from calendar import timegm
from datetime import datetime
from dateutil import tz

BLEACH_ATTR = bleach.ALLOWED_ATTRIBUTES.copy()
BLEACH_ATTR['img'] = ['src']
BLEACH_ATTR['time'] = ['*']

def filter(data):
    return bleach.clean(
       data,
       tags=bleach.ALLOWED_TAGS+['img','br','p','h4','h5','h6','span','time'],
       attributes=BLEACH_ATTR)

#os.exit(0)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rss_test.settings")
django.setup()

from feed.models import *

txt=""

for feed in Feed.objects.all():
  print("Getting rss feed "+feed.link)
  try:
      d = feedparser.parse(feed.link)
  
      #print(d['feed'])
  
      # We want the defualt more restrictive filters for the title.
      feed.title = bleach.clean(d['feed']['title'])
      feed.url   = bleach.clean(d['feed']['link'])
  
      if 'published_parsed' in d['feed']:
        feed.updated = datetime.fromtimestamp(timegm(d['feed']['published_parsed']),tz=tz.tzutc())
      elif 'updated_parsed' in d['feed']:
        feed.updated = datetime.fromtimestamp(timegm(d['feed']['updated_parsed']),tz=tz.tzutc())
      if 'description' in d['feed']:  
        feed.description = filter(d['feed']['description'])
      feed.save()
      for item in d['entries']:
        #print(item)
        #print(item['title'])
        #item['published'],item['link'])
        
        post_query = Post.objects.filter(link=item['link'])
        if post_query.exists():
            post = post_query.first()
        else:
            post = Post(feed=feed,title=bleach.clean(item['title']), link=item['link'])
        if 'published_parsed' in item:
          post.published = datetime.fromtimestamp(timegm(item['published_parsed']),tz=tz.tzutc())
        elif 'updated_parsed' in item:
          post.published = datetime.fromtimestamp(timegm(item['updated_parsed']),tz=tz.tzutc())
        if 'description' in item:    
          post.description = filter(item['description'])
          txt=filter(item['description'])
        post.save()
  except Exception:
     traceback.print_exc(file=sys.stderr)
     print(txt)