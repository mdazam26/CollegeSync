from django.db import models
from director.models import Batch, Branch, ClassGroup, Teacher
from semester.models import SemesterSubject, StudentClass, Subject, ActiveClassSemester


# Create your models here.
class PeriodSlot(models.Model):
    name = models.CharField(max_length=50)  # e.g., Period 1
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class Day(models.Model):
    name = models.CharField(max_length=20)  # e.g., Monday

    def __str__(self):
        return self.name

class ClassSchedule(models.Model):
    active_semester = models.ForeignKey(ActiveClassSemester, on_delete=models.CASCADE, null= True, blank= True,related_name='class_schedules')
    day = models.ForeignKey(Day, on_delete=models.CASCADE, null= True, blank= True)
    period = models.ForeignKey(PeriodSlot, on_delete=models.CASCADE, null= True, blank= True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='teachers', null=True, blank=True)

    # These two fields will be filled later by HOD
    subject = models.ForeignKey(SemesterSubject, null=True, blank=True, on_delete=models.SET_NULL)
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('active_semester', 'day', 'period')

    def __str__(self):
        cg = self.active_semester.class_group
        return f"{cg.branch.branch_name} | {cg.batch.batch_name} | {self.day.name} | {self.period.name}"
    

class ClassSchedule2(models.Model):
    active_semester2 = models.ForeignKey(ActiveClassSemester, on_delete=models.CASCADE, null= True, blank= True,related_name ='class_schedules2')
    day2 = models.ForeignKey(Day, on_delete=models.CASCADE, null= True, blank= True)
    period2 = models.ForeignKey(PeriodSlot, on_delete=models.CASCADE, null= True, blank= True)
    branch2 = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='teachers2', null=True, blank=True)

    # These two fields will be filled later by HOD
    subject2 = models.ForeignKey(SemesterSubject, null=True, blank=True, on_delete=models.SET_NULL)
    teacher2 = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('active_semester2', 'day2', 'period2')

    def is_teacher_available(self):
        if not self.teacher2 or not self.day2 or not self.period2:
            return False  # Incomplete info

        # Look for any other schedule at the same time with the same teacher
        conflict = ClassSchedule2.objects.filter(
            teacher2=self.teacher2,
            day2=self.day2,
            period2=self.period2
        ).exclude(id=self.id).exists()

        return not conflict
