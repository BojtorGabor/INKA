from django.contrib import admin
from django.urls import path, include

from django.contrib.auth.models import User

from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin

from innovativ.models import Position, Job, Project, PositionProject, EmailTemplate


class OTPAdmin(OTPAdminSite):
    pass


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    ordering = ['name']


class JobAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'id')
    ordering = ['user', 'position']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'view_name', 'id')
    ordering = ['name', 'view_name']


class PositionProjectAdmin(admin.ModelAdmin):
    list_display = ('position', 'project', 'id')
    ordering = ['position', 'project']


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'id')
    ordering = ['title']


admin_site = OTPAdmin(name='OTPAdmin')
admin_site.register(User)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)
admin_site.register(Position, PositionAdmin)
admin_site.register(Job, JobAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(PositionProject, PositionProjectAdmin)
admin_site.register(EmailTemplate, EmailTemplateAdmin)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('innovativ.urls')),
    path('tinymce/', include('tinymce.urls')),
]
