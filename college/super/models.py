from django.db import models

# Create your models here.

class College(models.Model):
    institute_name = models.CharField(max_length=100)
    institute_address = models.TextField()
    institute_email = models.EmailField()
    institute_number = models.CharField(max_length=15)

    admin_name = models.CharField(max_length=50)
    admin_number = models.CharField(max_length=15)
    admin_email = models.EmailField()
    admin_username = models.CharField(max_length=11, unique=True)
    admin_password = models.CharField(max_length=20)


def __str__(self):
    return f"{self.institute_name} ({self.admin_name} - {self.admin_number}) "
