from django.urls import path
from . import views, views_members


urlpatterns = [
    path('', views.home, name='home'),
    path('login', views_members.login_user, name='login'),
    path('logout', views_members.logout_user, name='logout'),
    path('register', views_members.register_user, name='register'),
    path('update_password', views_members.update_password, name='update-password'),

    path('<str:project_name>/', views.projects, name='projects'),
]
