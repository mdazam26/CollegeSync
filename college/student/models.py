from django.db import models
from director.models import ClassGroup

# Student stores basic profile info
class Student(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    student_name = models.CharField(max_length=200, null=True, blank=True)
    student_roll = models.CharField(max_length=10, null=True, blank=True)
    student_email = models.EmailField(unique=True, null=True, blank=True)
    student_phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    student_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    student_dob = models.DateField(null=True, blank=True)
    student_enrollment_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    student_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} ({self.student_enrollment_number})"

# StudentClass links student to a specific class (ClassGroup)
class StudentClass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='student_classes')
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name='students')

    class Meta:
        unique_together = ('student', 'class_group')

    def __str__(self):
        return f"{self.student.student_name} - {self.class_group} (Roll: {self.student.student_roll})"
