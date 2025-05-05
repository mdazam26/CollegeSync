from django.urls import path, include
from . import views


urlpatterns = [
    path('',views.index),


    path('open_director_login/', views.open_director_login, name='open_director_login'),


    path('director_login/', views.director_login, name='director_login'),

    path('director_dashboard/', views.director_dashboard, name='director_dashboard'),
    path('director_logout', views.director_logout, name='director_logout'),

    path('create_teacher_form/', views.create_teacher_form, name='create_teacher_form'),
    path('create_teacher/', views.create_teacher, name='create_teacher'),
    path('view_teacher/', views.view_teacher, name='view_teacher'),
    path('goto_manage_teacher/<int:teacher_id>/', views.goto_manage_teacher, name='goto_manage_teacher'),
    path('manage_teacher/<int:teacher_id>/', views.manage_teacher, name='manage_teacher'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    

    path('create_batch_form/', views.create_batch_form, name='create_batch_form'),
    path('create_batch/', views.create_batch, name='create_batch'), 
    path('view_batch/', views.view_batch, name='view_batch'),
    path('goto_manage_batch/<int:batch_id>', views.goto_manage_batch, name='goto_manage_batch'),
    path('manage_batch/<int:batch_id>/', views.manage_batch, name='manage_batch'),
    path('delete_batch/<int:batch_id>/', views.delete_batch, name='delete_batch'),


    path('create_branch_form/',views.create_branch_form, name='create_branch_form' ),
    path('create_branch/', views.create_branch, name='create_branch'),
    path('view_branch/', views.view_branch, name='view_branch'),  
    path('goto_manage_branch/<int:branch_id>/', views.goto_manage_branch, name='goto_manage_branch'), 
    path('manage_branch/<int:branch_id>', views.manage_branch, name='manage_branch'),
    path('delete_branch/<int:branch_id>/', views.delete_branch, name='delete_branch'),

    
    path('create_class_form/', views.create_class_form, name='create_class_form'),
    path('create_class/', views.create_class, name='create_class'),
    path('view_class/', views.view_class, name='view_class'),
    path('delete_class/<int:class_id>/', views.delete_class, name='delete_class'),
 

    # path('create_student_from/', include('student.urls'))

]