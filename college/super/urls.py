from django.urls import path, include
from . import views



urlpatterns = [
 
    path('',views.main),

    path('create/', views.create, name='create'),
    path('open_create/', views.open_create, name='open_create'),

    path('view/',views.view, name='view'),
    path('manage/', views.manage, name='manage'),
]
