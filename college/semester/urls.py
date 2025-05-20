from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [

    path('', views.index, name='goto_semester'),


    path('create_semesterTemplate_form/', views.create_semesterTemplate_form, name='create_semesterTemplate_form'),

    path('create_semesterTemplate/', views.create_semesterTemplate, name='create_semesterTemplate'),
    
    path('create_branchSemester_form/', views.create_branchSemester_form, name='create_branchSemester_form'),
    path('create_branchSemester/', views.create_branchSemester, name='create_branchSemester'),

    path('create_subject_form/', views.create_subject_form, name='create_subject_form'),
    path('create_subject/', views.create_subject, name='create_subject'),
    path('goto_manage_subject/<int:subject_id>/', views.goto_manage_subject, name='goto_manage_subject'),
    path('manage_subject/<int:subject_id>/', views.manage_subject, name='manage_subject'),
    path('delete_subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),

    path('create_semesterSubject_form/', views.create_semesterSubject_form, name='create_semesterSubject_form'),
    path('create_semesterSubject/', views.create_semesterSubject, name='create_semesterSubject'),

    path('create_subjectAssign_form/', views.create_subjectAssign_form, name='create_subjectAssign_form'),
    path('create_subjectAssign', views.create_subjectAssign, name='create_subjectAssign'),

    path('create_activeClassSemester_form/', views.create_activeClassSemester_form, name='create_activeClassSemester_form'),
    path('create_activeClassSemester/', views.create_activeClassSemester, name='create_activeClassSemester'),
    path('goto_manage_activeClassSemester/<int:acs_id>/', views.goto_manage_activeClassSemester, name='goto_manage_activeClassSemester'),
    path('manage_activeClassSemester/<int:acs_id>/', views.manage_activeClassSemester,   name='manage_activeClassSemester'),
    path('delete_activeClassSemester/<int:acs_id>/', views.delete_activeClassSemester, name='delete_activeClassSemester'),
]