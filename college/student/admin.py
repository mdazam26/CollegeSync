from django.contrib import admin

# Register your models here.

from .models import Student, StudentClass

admin.site.register(Student)
admin.site.register(StudentClass)