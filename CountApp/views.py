import json
import requests
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import requests
# Create your views here.
def index(request):
    return render(request,'index.html')

def check_sso(request):

    DISQUS_SECRET_KEY = 'saS4ySxgxB3u8H0u4y8DVBgqRwB5AE0sKafxS3z2pk3v0KJHEFNmf7O5X6h5aRak'
    DISQUS_PUBLIC_KEY = 'HwMMeRJh7M0sEUvQTKc9WD1y7XxZUA4Ft9ITOATNOxnZrQ5JmsZ3EZfxRwViiHaA'

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
        name:   "OneCount",
        
        url:     "https://django-disqus.herokuapp.com/loginprocess",
        logout:  "http://www.screener.in/logout/",
        };
    }
    </script>""" % dict(
            message=message,
            timestamp=timestamp,
            sig=sig,
            pub_key=DISQUS_PUBLIC_KEY
        )


    if request.user:
        sso = get_sso_auth(request.user)
    return render(request, "check_sso.html", {"disqus_sso": sso})


def registration(request):
    msg = None
    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        if cpassword == password:
            json_data = {
                "Users":
                    {
                        "PartnerId": 0,
                        "Demo": {
                            "1": email,
                            "2": username,
                            "3": password,

                        }

                    },
                "DedupeColumns": "1",

                "Transactions": [],

                "Return": "1"
            }
            response = requests.post('https://api.onecount.net/v2/users', json=json_data,headers={"Appkey":"a6de8a39b2ad34a5f6dc947021ea02c1025bfd3e"})

            print("Status code: ", response.status_code)
            print("Printing Entire Post Request")

            if response.json()['result']['success'] == "1":
                msg = " Successfully Registered "
                messages.success(request,msg)
                print(response.json()['Users']["Id"])

                return redirect("loginprocess")
            else:
                msg = response.json()['result']['error']['message']
                messages.error(request, msg)
        else:
            messages.error(request,"Please enter same password and confirm password")

    return render(request,'SignUp.html')

def loginprocess(request):
    if 'user' not in request.session:
        msg = None
        if request.method == "POST":

                email = request.POST['email']
                password = request.POST['password']

                json_data = {
                    "e": email, "p": password
                }
                response = requests.post('https://api.onecount.net/v2/users/login', json=json_data,
                                         headers={"Appkey": "a6de8a39b2ad34a5f6dc947021ea02c1025bfd3e"})

                print(response.json())
                if response.json()['result']['success'] == '1':
                    msg = " Successfully Logged In "
                    u_id = response.json()['Users'][0]
                    response = requests.get('https://api.onecount.net/v2/users/'+str(u_id),
                                             headers={"Appkey": "a6de8a39b2ad34a5f6dc947021ea02c1025bfd3e"})
                    request.session['user'] = response.json()['Users'][0]['OCID_HASH']
                    request.session['userData'] = response.json()['Users'][0]['Demo']['1']
                    messages.success(request, msg)
                    return redirect("Home")
                else:
                    msg = response.json()['result']['error']['message']
                    messages.error(request, msg)

        return render(request, 'login.html')
    else:
        return redirect("Home")

def logoutprocess(request):
    if request.user:
        if 'user' in request.session:
            del request.session['user']
            del request.session['userData']
        return redirect("Home")


