from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from feed.models import Post,Feed,PostGroup,PostGroupName,PostGroupQuery,FeedQuery
from calendar import timegm
from datetime import datetime
from dateutil import tz
import triceratops.settings
import json
import uuid
import django.contrib.auth

@login_required
#@csrf_exempt
def upload(request):
    print(request.FILES)
    fs = FileSystemStorage()
    filename = fs.save(str(uuid.uuid4()), request.FILES['file'])
    uploaded_file_url = fs.url(filename)

    return HttpResponse(json.dumps({'location' : uploaded_file_url}), content_type="application/json")

def login(request):
#    print("boop")
    # context = RequestContext(request, {
    #     'request': request, 'user': request.user})
    # return render_to_response('login.html', context_instance=context)
    return render(request, 'feed/templates/login.html')

def action(request):
    response=""
    if request.POST['action'] == 'logout':
        logout(request)
    elif request.POST['action'] == 'login':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            django.contrib.auth.login(request, user)
        else:
            response="login failed!"
    elif request.POST['action'] == 'like' and request.user.is_authenticated:
        post_rec = Post.objects.filter(link=request.POST['link'])
        tag_name = PostGroupName.objects.filter(name="#like")
        if request.POST['like'] == '1':
          print(post_rec.all())
          print(tag_name.all())
          tag = PostGroup.objects.create(post=post_rec.first(),owner=request.user,name=tag_name.first())
          #tag.save()
          print(tag)
        elif request.POST['like'] == '0':
          tag = PostGroup.objects.all().filter(owner=request.user).filter(name="#like").filter(post=post_rec.first())
          print(tag.all())
          tag.delete()
        resp = { "liked" : request.POST['like'] == '1' }
        response=json.dumps(resp)
    
    elif request.POST['action'] == 'delete' and request.user.is_authenticated:
        post = Post.objects.filter(link=request.POST['link']).first()
        #print(request.POST['link'])
        #print(post.all())

        resp = { "deleted" : post.safe_delete(request.user),
                 "feed" : post.feed.get_url(),
               }
        response=json.dumps(resp)
    elif request.POST['action'] == 'post' and request.user.is_authenticated:
        print(request.POST)
        feed = Feed.objects.filter(link='local://'+request.user.get_username()).first()
        
        post = Post(feed=feed,title='', link='local://'+str(uuid.uuid4()))
        post.content_type = request.POST['content_type']
        post.title = request.POST['title']
        post.description = request.POST['description']
        post.published = datetime.now()
        post.save()
        template = loader.get_template('feed/templates/index.html')
        render_html = template.render({
            'feed':[post],
            'login' : request.user.is_authenticated,
            'base_url' : triceratops.settings.BASE_URL
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
            'base_url' : triceratops.settings.BASE_URL
    }        
    if 'no_header' not in request.GET:
        context['header'] = True
    return HttpResponse(template.render(context, request))

def post(request,url):
    url="local://"+url
    feed = FeedQuery(Post.objects.filter(feed__enabled=True).filter(link=url),request.user)
    post = feed.first()
    
    if 'action' in request.POST and request.POST['action'] == 'update' and request.user.is_authenticated:
        post.content_type = request.POST['content_type']
        post.description = request.POST['description']
        post.title = request.POST['title']
        post.save()
    if 'json' in request.GET:
        output = json.dumps({ 
            "post": post.dict(),
            "html": get_feed(request,feed,template = loader.get_template('feed/templates/post.html')),
        })
        return HttpResponse(output, content_type="application/json")
    return HttpResponse(get_feed(request,feed,template = loader.get_template('feed/templates/post.html')))

def feed(request,url):
    if 'action' in request.POST:
        action(request)
        
    url="local://"+url
    feed = FeedQuery(Post.objects,request.user).filter(feed__enabled=True).filter(feed__link=url)
    return HttpResponse(get_feed(request,feed))
    
def tag(request,tag_name):
    if 'action' in request.POST:
        action(request)
    
    feed = FeedQuery(Post.objects,request.user).filter(feed__enabled=True).filter(tags__contains=[tag_name])
    return HttpResponse(get_feed(request,feed))
    
def index(request):
    if 'action' in request.POST:
        action(request)
        
    feed = FeedQuery(Post.objects,request.user).filter(feed__enabled=True)
    return HttpResponse(get_feed(request,feed))
    
def get_feed(request,feed_query,template = loader.get_template('feed/templates/index.html')):
    args = ''
    increment_amount = 10;
    max_items = 25
    feed_items = []
    
    print(request.is_secure())
    print(request.META)
    if not request.user.is_authenticated:
        feed_query = feed_query.filter(feed__public=True)
    else:
        if 'liked' in request.GET:
            feed_query = feed_query.liked().order_by("-published")
            #PostGroupQuery(PostGroup.objects.filter(owner=request.user).filter(name__name="#like").order_by("-post__published"))
#            
#            print(list(PostGroup.objects.all()))
            args = '&liked'
    
    if 'search' in request.GET:
        #feed_query = feed_query.filter(description__search=request.GET['search'])
        feed_query = feed_query.filter(search_vector_description=request.GET['search'])
        print("search:");print(request.GET['search']);
        args = args + '&search=' + request.GET['search']
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
            'base_url' : triceratops.settings.BASE_URL
    }        
    if 'no_header' not in request.GET:
        context['header'] = True
    
    return template.render(context, request)

def base(request):
    template = loader.get_template('feed/templates/base.html')
    context = {
            'login' : request.user.is_authenticated,
            'base_url' : triceratops.settings.BASE_URL
    }        
    if 'no_header' not in request.GET:
        context['header'] = True
    
    return HttpResponse(template.render(context, request))