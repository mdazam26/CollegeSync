from django.db import models
from schedule.models import ClassSchedule2

# Create your models here.
# class Teacher(models.Model):
#     def is_available(self, day, period):
#         return not ClassSchedule2.objects.filter(
#             day2=day,
#             period2=period,
#             teacher2=self
#         ).exists()