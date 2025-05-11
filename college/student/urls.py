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


    path('existing_students/', views.existing_students_form, name='existing_students_form'),
    
    path('add_existing_student/<int:classgroup_id>/', views.add_existing_student, name='add_existing_student'),

    path('classgroup_create_student_form/', views.classgroup_create_student_form, name='classgroup_create_student_form'),

    path('classgroup_create_student/', views.classgroup_create_student, name='classgroup_create_student'),

    path('classgroup_view_student/', views.classgroup_view_student, name='classgroup_view_student'),

    path('view_classgroup_student/<int:student_id>/', views.view_classgroup_student, name='view_classgroup_student'),

   # student/urls.py
    path('classgroup_students/<int:classgroup_id>/', views.classgroup_students_view, name='classgroup_students_view')

]