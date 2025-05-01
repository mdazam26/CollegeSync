from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
# Create your models here.

class Tenant(TenantMixin):
    # Add fields for your tenant, like name or other attributes
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    # Add other fields as needed
    # For example, you could add a field for the tenant's logo, etc.
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    

class TenantDomain(DomainMixin):
    # This model is used to map domains to tenants.
    # Add the domain and tenant association
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    domain = models.CharField(max_length=253)  # The domain, like tenant1.collegesync.com

    def __str__(self):
        return self.domain