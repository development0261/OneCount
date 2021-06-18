from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [

    path('',index,name="Home" ),
    path('check_sso/',check_sso,name="check_sso" ),
    path('register/',registration,name="registration" ),
    path('loginprocess/',loginprocess,name="loginprocess" ),
    path('logoutprocess/',logoutprocess,name="logoutprocess" ),

]