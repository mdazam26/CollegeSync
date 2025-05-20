from django.db import models
from schedule.models import ClassSchedule2
from student.models import Student
from semester.models import SemesterSubject, ActiveClassSemester
from director.models import Teacher


class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    active_class_semester = models.ForeignKey(ActiveClassSemester, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(SemesterSubject, on_delete=models.CASCADE, related_name='attendance_records')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_taken')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.student_name} | {self.subject.subject.name} | {self.date} | {self.status}"
