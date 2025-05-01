from django.db import models
from datetime import timedelta, date

# Default function for paid_until field
def default_paid_until():
    return date.today() + timedelta(days=30) 

class College(models.Model):
    
    schema_name = models.CharField(max_length=50, unique=True, null=True, blank=True)  # e.g., "macet"
    domain = models.CharField(max_length=100, unique=True, null=True, blank=True) 

    institute_name = models.CharField(max_length=100)

    institute_address = models.TextField(null=True, blank=True)

    institute_email = models.EmailField(null=True, blank=True)
    institute_number = models.CharField(max_length=15, null=True, blank=True)

    admin_name = models.CharField(max_length=50)
    admin_number = models.CharField(max_length=15, null=True, blank=True)
    admin_email = models.EmailField(null=True, blank=True)
    admin_username = models.CharField(max_length=11, unique=True)
    admin_password = models.CharField(max_length=150)

    paid_until = models.DateField(default=default_paid_until, null=True, blank=True)  # Made null and blank True
    on_trial = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.institute_name} ({self.admin_name} - {self.admin_number}) "
