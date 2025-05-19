from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='goto_schedule'),

    path('create_periodSlots_form/', views.create_periodSlots_form, name='create_periodSlots_form'),
    path('create_periodSlot/', views.create_periodSlot, name='create_periodSlot'),
    path('goto_manage_periodSlot/<int:period_id>/', views.goto_manage_periodSlot, name='goto_manage_periodSlot'),
    path('manage_periodSlot/<int:period_id>/', views.manage_periodSlot, name='manage_periodSlot'),
    path('delete_periodSlot/<int:period_id>/', views.delete_periodSlot, name='delete_periodSlot'),


    path('days/', views.days, name='days'), 

    path('create_classSchedule_form/', views.create_classSchedule_form, name='create_classSchedule_form'),
    path('create_classSchedule/', views.create_classSchedule, name='create_classSchedule'),
    path('goto_manage_classSchedule/<int:schedule_id>/', views.goto_manage_classSchedule, name='goto_manage_classSchedule'),
    path('manage_classSchedule/<int:schedule_id>/', views.manage_classSchedule, name='manage_classSchedule'),
    path('delete_classSchedule/<int:schedule_id>/', views.delete_classSchedule, name='delete_classSchedule'),

]