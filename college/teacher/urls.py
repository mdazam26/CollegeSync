from django.urls import path, include
from . import views




urlpatterns = [
    path('',views.professor_login_page, name='professor_login_page'),

    path('professor_login/',views.professor_login, name='professor_login' ),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('view_branch_students/', views.view_branch_students, name='view_branch_students'),
    path('logout/', views.professor_logout, name='professor_logout'),


    path('create_schedule_form', views.create_schedule_form, name='create_schedule_form'),
    path('create_schedule', views.create_schedule, name="create_schedule"),
    
]