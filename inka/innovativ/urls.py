from . import views_members, views, views_projects02, views_projects04, views_projects05

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),

    path('login', views_members.login_user, name='login'),
    path('logout', views_members.logout_user, name='logout'),
    path('register', views_members.register_user, name='register'),
    path('update_password', views_members.update_password, name='update_password'),

    path('<str:view_name>/<int:task_id>', views.view_names, name='view_names'),
    path('tasks/<str:filter>/<str:view_name>', views.tasks, name='tasks'),
    path('customer_price_offer/<int:price_offer_id>/', views.customer_price_offer, name='customer_price_offer'),

    path('p_02_1_telefonos_megkereses/<int:task_id>/', views_projects02.p_02_1_telefonos_megkereses,
         name='p_02_1_telefonos_megkereses'),
    path('p_02_1_telefonszam_keres/<int:task_id>/', views_projects02.p_02_1_telefonszam_keres,
         name='p_02_1_telefonszam_keres'),
    path('p_02_1_ugyfelnek_elozetes_arajanlat/<int:task_id>/', views_projects02.p_02_1_ugyfelnek_elozetes_arajanlat,
         name='p_02_1_ugyfelnek_elozetes_arajanlat'),
    path('p_02_1_ugyfelnek_felmeres/<int:task_id>/', views_projects02.p_02_1_ugyfelnek_felmeres,
         name='p_02_1_ugyfelnek_felmeres'),
    path('p_02_1_ugyfel_elerhetetlen/<int:task_id>/', views_projects02.p_02_1_ugyfel_elerhetetlen,
         name='p_02_1_ugyfel_elerhetetlen'),

    path('p_04_1_ugyfel_visszaadasa_02_nek/<int:task_id>/', views_projects04.p_04_1_ugyfel_visszaadasa_02_nek,
         name='p_04_1_ugyfel_visszaadasa_02_nek'),

    path('p_05_1_ugyfel_visszaadasa_02_nek/<int:task_id>/', views_projects05.p_05_1_ugyfel_visszaadasa_02_nek,
         name='p_05_1_ugyfel_visszaadasa_02_nek'),

    path('customers',views.customers, name='customers'),
    path('customer_history/<int:customer_id>/',views.customer_history, name='customer_history'),
    # path('projects', views.projects, name='projects'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
