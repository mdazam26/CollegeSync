from django.db import models
from student.models import StudentClass
from director.models import Branch, ClassGroup
# Create your models here.

class SemesterTemplate(models.Model):
    semester_name = models.CharField(max_length=10, unique= True, null= True, blank= True)

    def __str__(self):
        return self.semester_name

class BranchSemester(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="branch_semesters")
    semester_template = models.ForeignKey(SemesterTemplate, on_delete=models.CASCADE, related_name='branch_semesters')

    class Meta:
        unique_together = ('branch', 'semester_template')
    
    def __str__(self):
        return f"{self.branch.branch_name} - {self.semester_template.semester_name}"

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, null= True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    credit = models.IntegerField(null= True, blank= True)
    modules = models.IntegerField(null= True, blank= True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class SemesterSubject(models.Model):
    branch_semester = models.ForeignKey(
        BranchSemester,
        on_delete=models.CASCADE,
        related_name='semester_subjects'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='semester_usages'
    )

    class Meta:
        unique_together = ('branch_semester', 'subject')

    def __str__(self):
        return f"{self.branch_semester} → {self.subject.name}"

class ActiveClassSemester(models.Model):

    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name='active_semesters',
        null=True,
        blank=True
    )
    branch_semester = models.ForeignKey(
        BranchSemester,
        on_delete=models.CASCADE,
        related_name='active_class_semesters',
        null=True,
        blank=True
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('class_group', 'branch_semester')

    def __str__(self):
        return f"{self.class_group} → {self.branch_semester.semester_template.semester_name}"
