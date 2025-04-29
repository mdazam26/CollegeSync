from django.urls import path
from . import views


urlpatterns = [
    path('',views.index),


    path('open_login/', views.open_login, name='open_login'),


    path('director_login/', views.director_login, name='director_login'),

    path('director_dashboard/', views.director_dashboard, name='director_dashboard'),

]