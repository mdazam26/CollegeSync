from django.urls import path
from . import views


urlpatterns = [
    path('',views.index),


    path('open_login/', views.open_login, name='open_login'),


    path('director_login/', views.director_login, name='director_login'),

    path('director_dashboard/', views.director_dashboard, name='director_dashboard'),


    path('create_hod/', views.create_hod, name='create_hod'),
    path('manage_hod/', views.manage_hod, name='manage_hod'),

    path('create_batch/', views.create_batch, name='create_batch'),
    path('manage_batch/', views.manage_batch, name='manage_batch'),

    path('create_branch/', views.create_branch, name='create_branch'),
    path('manage_branch/', views.manage_branch, name='manage_branch'),

    path('director_logout', views.director_logout, name='director_logout'),

]