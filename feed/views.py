from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from feed.models import Post,Feed
from calendar import timegm
from datetime import datetime
from dateutil import tz
import rss_test.settings
import json
import uuid

@login_required
@csrf_exempt
def upload(request):
    print(request.FILES)
    fs = FileSystemStorage()
    filename = fs.save(str(uuid.uuid4()), request.FILES['file'])
    uploaded_file_url = fs.url(filename)

    return HttpResponse(json.dumps({'location' : uploaded_file_url}), content_type="application/json")
def action(request):
    response=""
    if request.POST['action'] == 'logout':
        logout(request)
    elif request.POST['action'] == 'login':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            response="login failed!"
    elif request.POST['action'] == 'like' and request.user.is_authenticated:
        post = Post.objects.filter(link=request.POST['link'])
        #print(request.POST['link'])
        #print(post.all())
        post = post.all()[0]
        post.liked = request.POST['like']
        post.save()
        
        resp = { "liked" : post.liked}
        response=json.dumps(resp)
    elif request.POST['action'] == 'post' and request.user.is_authenticated:
        print(request.POST)
        feed = Feed.objects.filter(link='local://'+request.user.get_username()).first()
        
        post = Post(feed=feed,title='', link='local://'+str(uuid.uuid4()))
        post.content_type = request.POST['content_type']
        post.description = request.POST['description']
        post.published = datetime.now()
        post.save()
        template = loader.get_template('feed/templates/index.html')
        render_html = template.render({
            'feed':[post],
            'login' : request.user.is_authenticated,
            'base_url' : rss_test.settings.BASE_URL
        }, request)
        response = json.dumps({ "html": render_html })
    else:
        print(request.POST)
    print("response:"+response)
    return HttpResponse(response, content_type="application/json")

@login_required
def feeds(request):
    template = loader.get_template('feed/templates/feeds.html')
    feeds = Feed.objects.all()
    args = ''
    
    context = {
            'feeds': feeds,
            'login' : request.user.is_authenticated,
            'args' : args,
            'base_url' : rss_test.settings.BASE_URL
    }        
    if 'no_header' not in request.GET:
        context['header'] = True
    return HttpResponse(template.render(context, request))

def post(request,url):
    url="local://"+url
    feed = Post.objects.filter(feed__enabled=True).filter(link=url)
    post = feed.first()
    
    if 'action' in request.POST and request.POST['action'] == 'update' and request.user.is_authenticated:
        post.content_type = request.POST['content_type']
        post.description = request.POST['description']
        post.published = datetime.now()
        post.save()
    if 'json' in request.GET:
        return HttpResponse(json.dumps({ "post": post.dict() }), content_type="application/json")
    return HttpResponse(get_feed(request,feed))

def feed(request,url):
    if 'action' in request.POST:
        action(request)
        
    url="local://"+url
    feed = Post.objects.filter(feed__enabled=True).filter(feed__link=url).order_by('-published')
    return HttpResponse(get_feed(request,feed))
    
def index(request):
    if 'action' in request.POST:
        action(request)
        
    feed = Post.objects.filter(feed__enabled=True).order_by('-published')
    return HttpResponse(get_feed(request,feed))
    
def get_feed(request,feed_query):
    args = ''
    increment_amount = 10;
    max_items = 25
    feed_items = []
    template = loader.get_template('feed/templates/index.html')
    
    if not request.user.is_authenticated:
        feed_query = feed_query.filter(feed__public=True)
    else:
        if 'liked' in request.GET:
            feed_query = feed_query.filter(liked=True)
            args = '&liked'
    if 'increment_amount' in request.GET:
        increment_amount = int(request.GET['increment_amount'])
        
    if 'timestamp' in request.GET:
        timestamp = datetime.fromtimestamp(int(request.GET['timestamp']),tz=tz.tzutc())
        feed_query = feed_query.filter(published__lt = timestamp)
    
    if 'max_items' in request.GET:
        max_items = int(request.GET['max_items'])
        
    if max_items>0 and feed_query.count() >0:
        feed_items = feed_query[:max_items].all()
        #print(feed.count(),max_items)
        item_overflow = { 'overflow' : max_items < feed_query.count(),
                          'last_item' : feed_items[len(feed_items)-1],
                          'last_timestamp' : timegm(feed_items[len(feed_items)-1].published.utctimetuple()),
                          'max_items' : max_items,
                          'max_items_incremented' : max_items + increment_amount,
                        }
    else:
        feed_items = feed_query.all()
        item_overflow = { 'overflow' : False }
    
    context = {
            'feed': feed_items,
            'item_overflow' : item_overflow,
            'login' : request.user.is_authenticated,
            'args' : args,
            'base_url' : rss_test.settings.BASE_URL
    }        
    if 'no_header' not in request.GET:
        context['header'] = True
    
    return template.render(context, request)

def base(request):
    template = loader.get_template('feed/templates/base.html')
    context = {
            'login' : request.user.is_authenticated,
            'base_url' : rss_test.settings.BASE_URL
    }        
    if 'no_header' not in request.GET:
        context['header'] = True
    
    return HttpResponse(template.render(context, request)) 