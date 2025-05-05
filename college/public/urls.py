from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='global_index'),
    path('tenant_form', views.tenant_form, name='tenant_form'),
    path('go-to-tenant/', views.go_to_tenant, name='go_to_tenant'),
]
