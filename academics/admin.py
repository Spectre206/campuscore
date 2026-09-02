from django.contrib import admin

from .models import (
    Assessment,
    AttendanceRecord,
    AttendanceSession,
    Course,
    Department,
    Enrollment,
    Grade,
    Program,
    Section,
)

admin.site.register(Department)
admin.site.register(Program)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Enrollment)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
admin.site.register(Assessment)
admin.site.register(Grade)
