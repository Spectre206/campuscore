from django.contrib import admin
from .models import Department, Program, Course, Section, Enrollment, AttendanceSession, AttendanceRecord, Assessment, Grade

admin.site.register(Department)
admin.site.register(Program)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Enrollment)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
admin.site.register(Assessment)
admin.site.register(Grade)