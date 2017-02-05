from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from feed.models import Post
from calendar import timegm
from datetime import datetime
from dateutil import tz
import json

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
    #print("response:"+response)
    return HttpResponse(response, content_type="application/json")
    
def index(request):
    increment_amount = 10;
    max_items = 25
    feed_items = []
    template = loader.get_template('feed/templates/index.html')
    feed = Post.objects.filter(feed__enabled=True).order_by('-published')

    if 'action' in request.POST:
        action(request)
    
    if not request.user.is_authenticated:
        feed = feed.filter(feed__public=True)
    
    if 'increment_amount' in request.GET:
        increment_amount = int(request.GET['increment_amount'])
        
    if 'timestamp' in request.GET:
        timestamp = datetime.fromtimestamp(int(request.GET['timestamp']),tz=tz.tzutc())
        feed = feed.filter(published__lt = timestamp)
    
    if 'max_items' in request.GET:
        max_items = int(request.GET['max_items'])
        
    if max_items>0:
        feed_items = feed[:max_items].all()
        #print(feed.count(),max_items)
        item_overflow = { 'overflow' : max_items < feed.count(),
                          'last_item' : feed_items[len(feed_items)-1],
                          'last_timestamp' : timegm(feed_items[len(feed_items)-1].published.utctimetuple()),
                          'max_items' : max_items,
                          'max_items_incremented' : max_items + increment_amount,
                        }
    else:
        feed_items = feed.all()
        item_overflow = { 'overflow' : False }
    
    context = {
            'feed': feed_items,
            'item_overflow' : item_overflow,
            'login' : request.user.is_authenticated
    }        
    if 'no_header' not in request.GET:
        context['header'] = True
    
    #if 'json' in request.GET:
    #    return json.dumps(context)
    return HttpResponse(template.render(context, request))
