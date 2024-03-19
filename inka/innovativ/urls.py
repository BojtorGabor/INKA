from django.urls import path
from . import views_members, views


urlpatterns = [
    path('', views.home, name='home'),

    path('login', views_members.login_user, name='login'),
    path('logout', views_members.logout_user, name='logout'),
    path('register', views_members.register_user, name='register'),
    path('update_password', views_members.update_password, name='update-password'),

    path('<str:project_name>/', views.project_names, name='project_names'),
    path('tasks', views.tasks, name='tasks'),
    path('projects', views.projects, name='projects'),
]
