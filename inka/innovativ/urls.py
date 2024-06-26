from . import views_members, views, views_crud, views_projects02, views_projects04, views_projects05

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),

    path('login', views_members.login_user, name='login'),
    path('logout', views_members.logout_user, name='logout'),
    path('register', views_members.register_user, name='register'),
    path('update_password', views_members.update_password, name='update_password'),
    path('change_position/<int:position_id>/', views_members.change_position, name='change_position'),

    path('<str:view_name>/<int:task_id>', views.view_names, name='view_names'),
    path('tasks/<str:filter>/<str:view_name>', views.tasks, name='tasks'),
    path('deadline_tasks', views.deadline_tasks, name='deadline_tasks'),
    path('feladat_hatarido/<int:task_id>/', views.feladat_hatarido, name='feladat_hatarido'),
    path('feladat_lezaras/<int:project_id>/<int:task_id>/', views.feladat_lezaras, name='feladat_lezaras'),
    path('feladat_keszites/<int:project_id>/<int:task_id>/', views.feladat_keszites, name='feladat_keszites'),

    path('customers', views.customers, name='customers'),
    path('customer_history/<int:customer_project_id>/', views.customer_history, name='customer_history'),
    path('customer_specify/<int:specify_id>/', views.customer_specify, name='customer_specify'),

    path('product_crud/',
         views_crud.product_crud, name='product_crud'),
    path('product_update/<int:product_id>/<str:action_name>/',
         views_crud.product_update, name='product_update'),
    path('product_group_crud/',
         views_crud.product_group_crud, name='product_group_crud'),
    path('product_group_update/<int:product_group_id>/<str:action_name>/',
         views_crud.product_group_update, name='product_group_update'),

    path('specifies/<str:status>/', views_projects05.specifies, name='specifies'),

    path('price_offer_update/<int:price_offer_id>/<int:project_id>/<int:task_id>/',
         views_crud.price_offer_update, name='price_offer_update'),
    path('price_offer_item_product/<int:price_offer_id>/<int:price_offer_item_id>/<int:project_id>/<int:task_id>/',
         views_crud.price_offer_item_product, name='price_offer_item_product'),
    path('price_offer_item_amount/<int:price_offer_id>/<int:price_offer_item_id>/<int:project_id>/<int:task_id>/',
         views_crud.price_offer_item_amount, name='price_offer_item_amount'),
    path('price_offer_item_price/<int:price_offer_id>/<int:price_offer_item_id>/<int:project_id>/<int:task_id>/',
         views_crud.price_offer_item_price, name='price_offer_item_price'),
    path('price_offer_comment/<int:price_offer_id>/<int:project_id>/<int:task_id>/',
         views_crud.price_offer_comment, name='price_offer_comment'),
    path('price_offer_change_money/<int:price_offer_id>/<int:project_id>/<int:task_id>/<str:change>/',
         views_crud.price_offer_change_money, name='price_offer_change_money'),
    path('price_offer_makepdf/<int:price_offer_id>/<int:project_id>/<int:task_id>/',
         views_crud.price_offer_makepdf, name='price_offer_makepdf'),

    path('p_02_1_telefonos_megkereses/<int:project_id>/<int:task_id>/',
         views_projects02.p_02_1_telefonos_megkereses, name='p_02_1_telefonos_megkereses'),
    path('p_02_1_telefonszam_keres/<int:project_id>/<int:task_id>/',
         views_projects02.p_02_1_telefonszam_keres, name='p_02_1_telefonszam_keres'),
    path('p_02_1_ugyfel_atadasa_04_1_nek/<int:project_id>/<int:task_id>/',
         views_projects02.p_02_1_ugyfel_atadasa_04_1_nek, name='p_02_1_ugyfel_atadasa_04_1_nek'),
    path('p_02_1_ugyfel_atadasa_05_1_nek/<int:project_id>/<int:task_id>/',
         views_projects02.p_02_1_ugyfel_atadasa_05_1_nek, name='p_02_1_ugyfel_atadasa_05_1_nek'),

    path('p_02_2_uj_feladat/',
         views_projects02.p_02_2_uj_feladat, name='p_02_2_uj_feladat'),
    path('p_02_2_uj_megkereses_igenye/<int:task_id>/',
         views_projects02.p_02_2_uj_megkereses_igenye, name='p_02_2_uj_megkereses_igenye'),

    path('p_04_1_elozetes_arajanlatok/<int:project_id>/<int:task_id>/',
         views_projects04.p_04_1_elozetes_arajanlatok, name='p_04_1_elozetes_arajanlatok'),
    path('p_04_1_elozetes_arajanlat_kuldes/<int:price_offer_id>/<int:project_id>/<int:task_id>/',
         views_projects04.p_04_1_elozetes_arajanlat_kuldes, name='p_04_1_elozetes_arajanlat_kuldes'),
    path('p_04_1_ugyfel_atadasa_05_1_nek/<int:project_id>/<int:task_id>/',
         views_projects04.p_04_1_ugyfel_atadasa_05_1_nek, name='p_04_1_ugyfel_atadasa_05_1_nek'),
    path('p_04_1_ugyfel_atadasa_02_1_nek/<int:project_id>/<int:task_id>/',
         views_projects04.p_04_1_ugyfel_atadasa_02_1_nek, name='p_04_1_ugyfel_atadasa_02_1_nek'),

    path('p_05_1_ugyfel_terkepre/<int:task_id>/',
         views_projects05.p_05_1_ugyfel_terkepre, name='p_05_1_ugyfel_terkepre'),
    path('p_05_1_process_coordinates/<int:customer_project_id>/',
         views_projects05.p_05_1_process_coordinates, name='p_05_1_process_coordinates'),
    path('p_05_1_ugyfel_atadasa_05_2_nek/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_1_ugyfel_atadasa_05_2_nek, name='p_05_1_ugyfel_atadasa_05_2_nek'),

    path('p_05_2_idopont_kereses/<int:task_id>/',
         views_projects05.p_05_2_idopont_kereses, name='p_05_2_idopont_kereses'),
    path('p_05_2_idopont_rogzites/<int:task_id>/',
         views_projects05.p_05_2_idopont_rogzites, name='p_05_2_idopont_rogzites'),
    path('p_05_2_felmero_rogzites/<int:task_id>/',
         views_projects05.p_05_2_felmero_rogzites, name='p_05_2_felmero_rogzites'),
    path('p_05_2_ugyfel_atadasa_05_3_nak/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_2_ugyfel_atadasa_05_3_nak, name='p_05_2_ugyfel_atadasa_05_3_nak'),
    path('p_05_2_ugyfel_atadasa_05_1_nek/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_2_ugyfel_atadasa_05_1_nek, name='p_05_2_ugyfel_atadasa_05_1_nek'),

    path('p_05_3_ugyfel_atadasa_05_4_nek/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_3_ugyfel_atadasa_05_4_nek, name='p_05_3_ugyfel_atadasa_05_4_nek'),
    path('p_05_3_ugyfel_atadasa_05_2_nek/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_3_ugyfel_atadasa_05_2_nek, name='p_05_3_ugyfel_atadasa_05_2_nek'),

    path('p_05_4_felmeresi_kepek_feltoltese/<int:task_id>/',
         views_projects05.p_05_4_felmeresi_kepek_feltoltese, name='p_05_4_felmeresi_kepek_feltoltese'),
    path('p_05_4_felmeresi_kepek_csoportositasa/<int:task_id>/',
         views_projects05.p_05_4_felmeresi_kepek_csoportositasa, name='p_05_4_felmeresi_kepek_csoportositasa'),
    path('p_05_4_felmeresi_kep_kivalasztasa/<int:task_id>/<int:specify_id>/',
         views_projects05.p_05_4_felmeresi_kep_kivalasztasa, name='p_05_4_felmeresi_kep_kivalasztasa'),
    path('p_05_4_felmeresi_kepek_tipusai/<int:task_id>/<int:specify_id>//<int:photo_id>/',
         views_projects05.p_05_4_felmeresi_kepek_tipusai, name='p_05_4_felmeresi_kepek_tipusai'),
    path('p_05_4_uj_felmeres_feladat_05_2_nek/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_4_uj_felmeres_feladat_05_2_nek, name='p_05_4_uj_felmeres_feladat_05_2_nek'),

    path('p_05_x_ugyfel_atadasa_02_1_nek/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_x_ugyfel_atadasa_02_1_nek, name='p_05_x_ugyfel_atadasa_02_1_nek'),
    path('p_05_x_ugyfel_atadasa_04_1_nek/<int:project_id>/<int:task_id>/',
         views_projects05.p_05_x_ugyfel_atadasa_04_1_nek, name='p_05_x_ugyfel_atadasa_04_1_nek'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
