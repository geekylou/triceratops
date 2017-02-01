import django
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rss_test.settings")
django.setup()

from feed.models import *

if sys.argv[1] == 'export':
    for feed in Feed.objects.all():
        print(feed.link)
elif sys.argv[1] == 'import':
    for line in sys.stdin:
        feed = Feed(link=line,title="")
        feed.save()