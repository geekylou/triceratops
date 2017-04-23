from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from feed_profile.models import Profile
from django.shortcuts import render

import triceratops.settings
# Create your views here.

def index(request,url):
    #url="local://"+url
    profile = Profile.objects.filter(user__username=url)
    
    template = loader.get_template('feed_profile/templates/index.html')

    print(profile.first())
    context = {
        'profile': profile.first(),
        'login' : request.user.is_authenticated,
#        'args' : args, # No args are used yet! [TODO] We probably won't ever need any for profiles.
        'base_url' : triceratops.settings.BASE_URL
        }
    if 'no_header' not in request.GET:
        context['header'] = True
            
    return HttpResponse(template.render(context, request))