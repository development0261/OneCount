import json

from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import login,logout,authenticate
from .forms import MyRegister,LoginForm
# Create your views here.
def index(request):

    return render(request,'index.html')

def check_sso(request):

    DISQUS_SECRET_KEY = 'sV40p5ZCNesXC14qjtleBkHSjcBVc9ALAFdGUvjWNuxrUejP9hwUvVxvB1XKXbM1'
    DISQUS_PUBLIC_KEY = 'Y0GFE8flXjkbeQvknIfnWLlxU72KFyyOQlKmwE2UJp6Z3RgIXBbWMzDd1HnVyyVB'

    import base64
    import hashlib
    import hmac
    import time
    import json
    import logging

    def get_sso_auth(user):
        # avoid conflicts with production users

        if user and user.is_authenticated:
            data = json.dumps({
                'id': user.id,
                'username': user.username,
                'email': user.email,
            })
        else:
            # sending empty json object logs out
            data = json.dumps({})

        # encode the data to base64
        message = base64.b64encode(data.encode('utf-8')).decode()
        # generate a timestamp for signing the message
        timestamp = int(time.time())
        # generate our hmac signature
        sig = hmac.HMAC(DISQUS_SECRET_KEY.encode('utf-8'), '{} {}'.format(message, timestamp).encode('utf-8'), hashlib.sha1).hexdigest()

        return """<script type="text/javascript">
    var disqus_config = function() {
        this.page.remote_auth_s3 = "%(message)s %(sig)s %(timestamp)s";
        this.page.api_key = "%(pub_key)s";
        this.page.url = '';
        this.sso = {
        name:   "Django Disqus",
        
        url:     "http://localhost:8000/register",
        logout:  "http://www.screener.in/logout/",
        };
    }
    </script>""" % dict(
            message=message,
            timestamp=timestamp,
            sig=sig,
            pub_key=DISQUS_PUBLIC_KEY
        )
    print(request.user)

    sso = get_sso_auth(request.user)
    return render(request, "check_sso.html", {"disqus_sso": sso})


def registration(request):
    if request.method == "POST":
        form = MyRegister(request.POST)
        if form.is_valid():
            form.save()
    form = MyRegister()
    return render(request,'signup.html',{'form':form})

def loginprocess(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
        return redirect("Home")

    return render(request, 'login.html')

def logoutprocess(request):
    if request.user:
        logout(request)
        return redirect("Home")


