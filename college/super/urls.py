from django.urls import path, include
from . import views



urlpatterns = [
 
    path('',views.main),
    path('create/', views.create, name='create'),
    path('view/',views.view, name='view'),
    path('manage/', views.manage, name='manage'),
]
