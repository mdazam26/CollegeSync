from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='goto_student'),


    path('create_student_form/', views.create_student_form, name='create_student_form'),
    path('create_student/', views.create_student, name='create_student'),
    path('view_student/', views.view_student, name='view_student'),
    path('goto_manage_student/<int:student_id>/', views.goto_manage_student, name='goto_manage_student'),
    path('manage_student/<int:student_id>/', views.manage_student, name='manage_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
]