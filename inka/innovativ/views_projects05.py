from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from innovativ.forms_projects import ReasonForm
from innovativ.models import Task, Project, CustomerProject, Specify

import folium


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


def p_05_1_idopont_kereses(request, task_id):
    task = Task.objects.get(pk=task_id)

    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        # Felmérésre várakozók kigyűjtése
        # Lekérdezzük az összes Specify rekordot, amelyek status mezője '1:' vagy '2:' vagy '4:'
        specify_records = Specify.objects.filter(Q(status='1:') | Q(status='2:') | Q(status='4:'))

        # Lekérdezzük az összes CustomerProject rekordot, amelyek az előző Specify rekordok customer_project-jei közé esnek
        customer_projects = CustomerProject.objects.filter(id__in=specify_records.values_list('customer_project', flat=True))

        # Várakozók térképe
        m1 = folium.Map(location=[47.2, 19.4], zoom_start=7)
        for customer_project in customer_projects:
            if task.customer_project.id == customer_project.id:
                folium.Marker([customer_project.latitude, customer_project.longitude],
                              popup=folium.Popup(f'{customer_project.customer} - {customer_project}',
                                                 max_width=250),
                              icon=folium.Icon(color='red', icon='info-sign')).add_to(m1)
            else:
                folium.Marker([customer_project.latitude, customer_project.longitude],
                              popup=folium.Popup(f'{customer_project.customer} - {customer_project}',
                                                 max_width=250),
                              icon=folium.Icon(color='blue', icon='info-sign')).add_to(m1)
        m1 = m1._repr_html_()  # HTML-reprezentáció

        # Egyeztetett felmérések kigyűjtése
        # Lekérdezzük az összes Specify rekordot, amelyek status mezője '3:'
        today = timezone.now().date()
        specify_records = Specify.objects.filter(Q(status='3:') & Q(specify_date__gt=today))

        # Lekérdezzük az összes CustomerProject rekordot, amelyek az előző Specify rekordok customer_project-jei közé esnek
        customer_projects = CustomerProject.objects.filter(id__in=specify_records.values_list('customer_project', flat=True))

        # Létrehozunk egy dictionary-t, amely a customer_project azonosítókat és specify_date értékeket párosítja
        customer_project_dates = dict(specify_records.values_list('customer_project', 'specify_date'))

        # Egyeztetett felmérések térképe
        m2 = folium.Map(location=[47.2, 19.4], zoom_start=7)
        for customer_project in customer_projects:
            # Itt hozzárendeljük a megfelelő specify_date értéket a CustomerProject objektumhoz
            specify_date = customer_project_dates.get(customer_project.id)
            formatted_specify_date = specify_date.strftime("%Y-%m-%d %H:%M")  # A kívánt formátumban formázzuk az időt

            # Készítünk egy Popup objektumot, amely tartalmazza a szükséges információkat
            popup_content = f'{customer_project.customer} - {customer_project}<br>' \
                            f'{formatted_specify_date}'  # Újsor karakterrel választjuk el az adatokat

            folium.Marker([customer_project.latitude, customer_project.longitude],
                          popup=folium.Popup(popup_content, max_width=250),
                          icon=folium.Icon(color='blue', icon='info-sign')).add_to(m2)
        # Plusz a mostani ügyfél pirossal
        folium.Marker([task.customer_project.latitude, task.customer_project.longitude],
                      popup=folium.Popup(f'{task.customer_project.customer} - {task.customer_project}',
                                         max_width=250),
                      icon=folium.Icon(color='red', icon='info-sign')).add_to(m2)
        m2 = m2._repr_html_()  # HTML-reprezentáció

        return render(request, '05/p_05_1_idopont_kereses.html', {'task': task,
                                                                  'map1': m1, 'map2': m2})


def p_05_1_ugyfel_visszaadasa_02_nek(request, task_id):
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

        return render(request, '05/p_05_1_ugyfel_visszaadása_02_nek.html', {'task': task, 'form': form})


def p_05_1_ugyfel_visszaadasa_04_nek(request, task_id):
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

        return render(request, '05/p_05_1_ugyfel_visszaadása_04_nek.html', {'task': task, 'form': form})