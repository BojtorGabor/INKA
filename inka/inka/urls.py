from django.contrib import admin
from django.urls import path, include

from django.contrib.auth.models import User

from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin

from innovativ.models import Position, Job, Project, ProjectPosition, Task


class OTPAdmin(OTPAdminSite):
    pass


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)


class JobAdmin(admin.ModelAdmin):
    list_display = ('user', 'position',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProjectPositionAdmin(admin.ModelAdmin):
    list_display = ('project','position')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'comment', 'created_at',)


admin_site = OTPAdmin(name='OTPAdmin')
admin_site.register(User)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)
admin_site.register(Position, PositionAdmin)
admin_site.register(Job, JobAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(ProjectPosition, ProjectPositionAdmin)
admin_site.register(Task, TaskAdmin)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('innovativ.urls'))
]
