from django.contrib import admin
from .models import Tenant, TenantDomain

# Register your models here.
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on')  # Add other fields you want to display
    search_fields = ('name',)  # Enable search by tenant name

@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'domain')  # Display tenant and domain
    search_fields = ('domain',)  # Enable search by domain