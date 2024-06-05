from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from innovativ.forms_projects import ReasonForm, DateInputForm
from innovativ.models import Task, Project, CustomerProject, Specify

import folium

from datetime import datetime, timedelta


def p_05_1_ugyfel_terkepre(request, task_id):
    task = Task.objects.get(pk=task_id)
    m = folium.Map(location=[47.2, 19.4], zoom_start=8)  # Alapértelmezett hely

    # if task.customer_project.latitude and task.customer_project.longitude:
    #     # Marker hozzáadása a térképhez
    #     folium.Marker(
    #         location=[task.customer_project.latitude, task.customer_project.longitude],
    #         popup=folium.Popup(f'{task.customer_project.customer}', max_width=200),
    #         icon=folium.Icon(color='blue', icon='info-sign')
    #     ).add_to(m)

    # A térkép HTML generálása
    map_html = m._repr_html_()
    # map_html = m.get_root().render()

    # Az Új feladat jelzőből Folyamatban jelző lesz
    task.type = '3:'
    task.type_color = '3:'
    task.save()

    return render(request, '05/p_05_1_ugyfel_terkepre.html', {'task': task, 'map_html': map_html})


def p_05_1_process_coordinates(request, customer_project_id):
    if request.method == 'POST':
        customer_project = CustomerProject.objects.get(pk=customer_project_id)

        lat = request.POST.get('lat')
        lng = request.POST.get('lng')

        #  Koordináták mentése
        customer_project.latitude = lat
        customer_project.longitude = lng
        customer_project.save()

        return JsonResponse({'status': 'success', 'latitude': lat, 'longitude': lng})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def p_05_1_ugyfel_felmeres_egyezetesre(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if task.customer_project.latitude == 0 or task.customer_project.longitude == 0:
            messages.success(request, 'Amíg nincs az ügyfél telepítési címe a térképre helyezve,'
                                      ' addig nem továbbíthatod felmérés egyeztetésre.')
            return render(request, 'home.html', {})
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                # Felmérés rekord létrehozása
                Specify.objects.create(customer_project=task.customer_project,
                                       status='1:',  # ügyfél project azonosító
                                       created_user=request.user)
                # Eredeti task lezárása
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat átdása 05.2. Ügyfél egyeztetés felmérésnek
                next_project = Project.objects.filter(name__startswith='05.2.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél project azonosító
                                    comment=f'{ task.customer_project.customer } - ügyfelünkkel egyeztethetsz felmérést.\n'
                                            f'{form["reason"].value()}',
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_1_ugyfel_felmeres_egyezetesre.html', {'task': task, 'form': form})



def p_05_2_idopont_kereses(request, task_id):
    task = Task.objects.get(pk=task_id)

    today = timezone.now().date()
    specify_records = (Specify.objects.filter(Q(status='1:') | Q(status='2:') | Q(status='3:') | Q(status='4:'),
                                              Q(specify_date__isnull=True) | Q(specify_date__gte=today))
                       .order_by('specify_date'))

    p = Paginator(specify_records, 10)
    page = request.GET.get('page', 1)
    specify_records_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        m1 = folium.Map(location=[47.2, 19.4], zoom_start=7)
        if request.method == 'POST':
            form = DateInputForm(request.POST)
            if form.is_valid():
                action = request.POST.get('action')
                if action == 'map':
                    input_date = form.cleaned_data['dateinput']
                    # Kezdő dátum és vég dátum meghatározása
                    start_date = timezone.make_aware(datetime.combine(input_date, datetime.min.time()))
                    end_date = timezone.make_aware(datetime.combine(input_date + timedelta(days=1), datetime.min.time()))

                    # Akiknek már van időpontjuk - térképre
                    map_records = (Specify.objects.filter(Q(status='1:') | Q(status='2:') | Q(status='3:') | Q(status='4:'),
                                               specify_date__gte=start_date, specify_date__lt=end_date))
                    for map_record in map_records:
                        # Készítünk egy Popup objektumot, amely tartalmazza a szükséges információkat
                        local_time = timezone.localtime(map_record.specify_date)
                        formatted_specify_date = local_time.strftime("%Y-%m-%d %H:%M")
                        popup_content = (f'{map_record.customer_project.customer} - {map_record.customer_project}<br>'
                                         f'{formatted_specify_date}')  # Újsor karakterrel választjuk el az adatokat
                        folium.Marker([map_record.customer_project.latitude,
                                       map_record.customer_project.longitude],
                                      popup=folium.Popup(popup_content, max_width=250),
                                      icon=folium.Icon(color='blue', icon='info-sign')).add_to(m1)

                    # Akiknek még nincs időpontjuk - térképre
                    map_records = Specify.objects.filter(Q(status='1:') | Q(status='2:') | Q(status='3:') | Q(status='4:'),
                                               specify_date__isnull=True)
                    for map_record in map_records:
                        # Készítünk egy Popup objektumot, amely tartalmazza a szükséges információkat
                        popup_content = f'{map_record.customer_project.customer} - {map_record.customer_project}'
                        folium.Marker([map_record.customer_project.latitude,
                                       map_record.customer_project.longitude],
                                      popup=folium.Popup(popup_content, max_width=250),
                                      icon=folium.Icon(color='green', icon='info-sign')).add_to(m1)

                    # Az aktuális ügyfél project - térképre
                    folium.Marker([task.customer_project.latitude,
                                   task.customer_project.longitude],
                                  popup=folium.Popup(f'{task.customer_project.customer} - '
                                                     f'{task.customer_project}', max_width=250),
                                  icon=folium.Icon(color='red', icon='info-sign')).add_to(m1)
                    m1 = m1._repr_html_()  # HTML-reprezentáció
                elif action == "ready":
                    return render(request, 'home.html', {})
        else:
            initial_data = {'dateinput': datetime.now()}
            form = DateInputForm(initial=initial_data)

        return render(request, '05/p_05_2_idopont_kereses.html',
                      {'task': task, 'form': form, 'specify_records': specify_records_page, 'map': m1,
                       'page_list': specify_records_page, 'page_range': page_range, })


def p_05_2_idopont_rogzites(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                # Eredeti task lezárása
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat visszaadása 05.1. Felmérése felelőséhez
                next_project = Project.objects.filter(name__startswith='05.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél azonosító
                                    comment=f'{task.customer_project.customer} - Kérek egy új térképre illesztést.\n'
                                            f'{form["reason"].value()}',
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_2_idopont_rogzites.html',
                      {'task': task, 'form': form})


def p_05_2_ugyfel_visszaleptetese_05_1_nek(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                # Eredeti task lezárása
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat visszaadása 05.1. Felmérése felelőséhez
                next_project = Project.objects.filter(name__startswith='05.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél azonosító
                                    comment=f'{task.customer_project.customer} - Kérek egy új térképre illesztést.\n'
                                            f'{form["reason"].value()}',
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_2_ugyfel_visszaleptetese_05_1_nek.html',
                      {'task': task, 'form': form})


def p_05_x_ugyfel_visszaadasa_02_nek(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                # Eredeti task lezárása
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat visszaadása 02. Ügyfél adatainak felelőséhez
                next_project = Project.objects.filter(name__startswith='02.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél azonosító
                                    comment=f'{task.customer_project.customer} - A felmérés nem végezhető el.\n'
                                            f'{form["reason"].value()}',
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_x_ugyfel_visszaadasa_02_nek.html', {'task': task, 'form': form})


def p_05_x_ugyfel_visszaadasa_04_nek(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                # Eredeti task lezárása
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat visszaadása 04. Előzetes árajánlatok felelőséhez
                next_project = Project.objects.filter(name__startswith='04.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél azonosító
                                    comment=f'{task.customer_project.customer} - A felmérés nem végezhető el.\n'
                                            f'{form["reason"].value()}',
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_x_ugyfel_visszaadasa_04_nek.html', {'task': task, 'form': form})
