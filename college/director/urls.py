from django.urls import path
from . import views


urlpatterns = [
    path('',views.index),


    path('open_login/', views.open_login, name='open_login'),


    path('director_login/', views.director_login, name='director_login'),

    path('director_dashboard/', views.director_dashboard, name='director_dashboard'),


    path('create_hod_form/', views.create_hod_form, name='create_hod_form'),
    path('create_hod/', views.create_hod, name='create_hod'),
    path('manage_hod/', views.manage_hod, name='manage_hod'),
    path('view_hod/', views.view_hod, name='view_hod'),


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

    # View details + actions
    path('manage_branch/<int:branch_id>/', views.manage_branch, name='manage_branch'), # Edit branch details
    path('delete_branch/<int:branch_id>/', views.delete_branch, name='delete_branch'), # Delete branch


    path('director_logout', views.director_logout, name='director_logout'),

]