from django.db import models

class Teacher(models.Model):
    teacher_username = models.CharField(max_length=100, unique=True, null= True, blank= True)
    teacher_name = models.CharField(max_length=100, null= True, blank= True)
    teacher_email = models.EmailField(null= True, blank= True)
    teacher_phone = models.CharField(max_length=15, null= True , blank= True   )
    teacher_password = models.CharField(max_length=100)  # Consider using Django's built-in user system for real apps
    is_hod = models.BooleanField(default=False)

    def __str__(self):
        return self.teacher_name


class Branch(models.Model):
    branch_name = models.CharField(max_length=100, unique=True, null=True, blank= True)
    branch_hod = models.OneToOneField(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hod_of_branch'
    )

    def __str__(self):
        return self.branch_name


class Batch(models.Model):
    batch_name = models.CharField(max_length=100, null = True, blank= True)
    
    def __str__(self):
        return f"{self.batch_name} "


class ClassGroup(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, related_name='class_groups')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='class_groups')

    class Meta:
        unique_together = ('batch', 'branch')  # Prevent duplicates like (2021, CSE) being created twice

    def __str__(self):
        return f"{self.batch.batch_name} - {self.branch.branch_name}"

    @property
    def hod(self):
        return self.branch.branch_hod  # So you can access classgroup.hod directly
