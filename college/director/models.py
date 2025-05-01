from django.db import models


# Create your models here.
class Batch(models.Model):
    batch_name = models.IntegerField(unique=True)  # Academic year (e.g., 2021, 2022)
    
    def __str__(self):
        return f"Batch {self.batch_name}"
    



class HOD(models.Model):
    hod_name = models.CharField(max_length=100)
    hod_email = models.EmailField()
    hod_phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.hod_name} ({self.email})"


class Branch(models.Model):
    branch_name = models.CharField(max_length=100)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name="branches")
    hod = models.OneToOneField(HOD, on_delete=models.SET_NULL, null=True, blank=True, related_name="branch")

    def __str__(self):
        return f"{self.branch_name} - {self.batch.batch_name if self.batch else 'No Batch'}"