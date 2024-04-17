from django.urls import path
from . import views_members, views, views_projects02, views_projects

urlpatterns = [
    path('', views.home, name='home'),

    path('login', views_members.login_user, name='login'),
    path('logout', views_members.logout_user, name='logout'),
    path('register', views_members.register_user, name='register'),
    path('update_password', views_members.update_password, name='update_password'),

    path('<str:view_name>/<int:task_id>', views.view_names, name='view_names'),
    path('tasks/<str:filter>/<str:view_name>', views.tasks, name='tasks'),

    path('p_02_1_telefonszam_keres/<int:task_id>/', views_projects02.p_02_1_telefonszam_keres,
         name='p_02_1_telefonszam_keres'),
    path('p_02_1_telefonos_megkereses/<int:task_id>/', views_projects02.p_02_1_telefonos_megkereses,
         name='p_02_1_telefonos_megkereses'),
    path('p_02_1_ugyfel_elerhetetlen/<int:task_id>/', views_projects02.p_02_1_ugyfel_elerhetetlen,
         name='p_02_1_ugyfel_elerhetetlen'),

    path('customers',views.customers, name='customers'),
    path('customer_history/<int:customer_id>/',views.customer_history, name='customer_history'),
    # path('projects', views.projects, name='projects'),
]
