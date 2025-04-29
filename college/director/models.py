from django.db import models

# Create your models here.
class Batch(models.Model):
    batch_name = models.IntegerField(unique=True)  # Academic year (e.g., 2021, 2022)
    
    def __str__(self):
        return f"Batch {self.batch_name}"
    

class Branch(models.Model):
    name = models.CharField(max_length=100)  # Name of the branch (e.g., CSE, ME, etc.)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="branches")  
    # Associate each branch with a batch
    # You could add more fields if needed (like the number of students, etc.)

    def __str__(self):
        return f"{self.name} - {self.batch.year}"
    


class HOD(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="hod")  
    # HOD is assigned to a branch
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.branch.name} - {self.branch.batch.year})"