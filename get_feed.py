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
  if (not feed.link.startswith('local://')):
    print("Getting rss feed "+feed.link)
    try:
      d = feedparser.parse(feed.link)
  
      print(d['feed'])
  
      # We want the defualt more restrictive filters for the title.
      if 'title' in d['feed']:
        feed.title = bleach.clean(d['feed']['title'])
      if 'link' in d['feed']:
        feed.url   = bleach.clean(d['feed']['link'])
      else:
        sys.stderr.write(str(feed)+"\n")
      if 'published_parsed' in d['feed']:
        feed.updated = datetime.fromtimestamp(timegm(d['feed']['published_parsed']),tz=tz.tzutc())
      elif 'updated_parsed' in d['feed']:
        feed.updated = datetime.fromtimestamp(timegm(d['feed']['updated_parsed']),tz=tz.tzutc())
      if 'description' in d['feed']:  
        feed.description = filter(d['feed']['description'])
      feed.save()
      for item in d['entries']:
        #print(item['title'])
        #item['published'],item['link'])
        
        post_query = Post.objects.filter(link=item['link'])
        if post_query.exists():
            post = post_query.first()
        else:
            title=""
            if 'title' in item:
                title=item['title']
            post = Post(feed=feed,title=bleach.clean(title), link=item['link'])
        if 'published_parsed' in item:
          post.published = datetime.fromtimestamp(timegm(item['published_parsed']),tz=tz.tzutc())
        elif 'updated_parsed' in item:
          post.published = datetime.fromtimestamp(timegm(item['updated_parsed']),tz=tz.tzutc())
        if 'description' in item:    
          post.description = item['description']
          txt=filter(item['description'])
        if 'tags' in item:
          tag_list = []
          for tag in item['tags']:
            tag_list.append(tag.term[0:128])
          post.tags = tag_list
        post.metadata=item
        print("Metadata");print(post.metadata)
        try:
          post.save()
        except Exception:
          #sys.stderr.write(str(post.metadata))
          traceback.print_exc(file=sys.stderr)
    except Exception:
      traceback.print_exc(file=sys.stderr)
      sys.stderr.write(txt)
      
update_indexes()