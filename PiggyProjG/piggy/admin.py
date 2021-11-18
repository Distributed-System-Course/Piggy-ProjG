from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Plan)
admin.site.register(Project)
admin.site.register(Team)
admin.site.register(TeamWish)
