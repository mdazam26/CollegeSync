from django.contrib import admin

# Register your models here.

from .models import Batch, Branch, HOD

admin.site.register(Batch)
admin.site.register(Branch)
admin.site.register(HOD)
