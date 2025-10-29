# -*- encoding: utf-8 -*-

from django.urls import path
from .views import login_view, register_user, logout_user
#from django.contrib.auth.views import logout
from . import views

urlpatterns = [
    path('login/', login_view, name="login"),
  #  path('listar-empleados/', listar_empleados, name='listar_empleados'),
    path('register/', register_user, name="register"),


    #path('add/', views.person_create_view, name='person_add'),
    
   
   

    # path("logout/", LogoutView.as_view(), name="logout")  
     path("logout/", logout_user, name="logout")
]



