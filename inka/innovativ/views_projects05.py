from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from innovativ.forms_projects import ReasonForm
from innovativ.models import Task, Project, CustomerProject

import folium


def p_05_1_ugyfel_terkepre(request, task_id):
    task = Task.objects.get(pk=task_id)
    m = folium.Map(location=[47.2, 19.4], zoom_start=8)  # Alapértelmezett hely

    if task.customer_project.latitude and task.customer_project.longitude:
        # Marker hozzáadása a térképhez
        folium.Marker(
            location=[task.customer_project.latitude, task.customer_project.longitude],
            popup=folium.Popup(f'{task.customer_project.customer}', max_width=200),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # A térkép HTML generálása
    map_html = m._repr_html_()
    # map_html = m.get_root().render()

    # Mentjük a térkép HTML-t egy fájlba
    # map_path = 'terkep.html'
    # m.save(map_path)
    #
    # # Beolvassuk a mentett HTML-t
    # with open(map_path, 'r', encoding='utf-8') as f:
    #     map_html = f.read()

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