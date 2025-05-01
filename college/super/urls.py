from django.urls import path, include
from . import views



urlpatterns = [
 
    path('',views.main, name='name'),

    path('create/', views.create, name='create'),
    path('open_create/', views.open_create, name='open_create'),

    path('view/',views.view, name='view'),

    path('manage/<int:college_id>/', views.manage, name='manage'),
    path('manage_college/<int:college_id>/', views.manage_college, name='manage_college'),
    path('delete/<int:college_id>/', views.delete_college, name='delete_college'),

]
