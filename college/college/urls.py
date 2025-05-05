"""
URL configuration for college project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import domain_based_redirect

urlpatterns = [
    path('admin/', admin.site.urls), # admin
    
    path('start/', views.start),

  


    path('super/', include('super.urls')), #its redirect to control for superuser

    # path('',include('director.urls')),  
    # path('', include('public.urls')),
    # path('', views.domain_based_redirect, name='domain_based_redirect')

    path('', domain_based_redirect),
    path('public/', include('public.urls')),
    path('director/', include('director.urls')),
   
]
