import os
from inka import settings

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import Template, Context
from django.utils import timezone

from innovativ.forms_projects import ReasonForm, DateInputForm, SpecifyDateTimeForm, SpecifierForm, EmailTemplateForm, \
    SpecifyPhotoForm, SpecifyPhotoTypeForm
from innovativ.models import Task, Project, CustomerProject, Specify, EmailTemplate, Customer, SpecifyPhoto
from inka.settings import DEFAULT_FROM_EMAIL

import folium

from datetime import datetime, timedelta

from . import views as app_views


################################# 05.1. #################################
def p_05_1_ugyfel_terkepre(request, task_id):
    task = Task.objects.get(pk=task_id)
    m = folium.Map(location=[47.2, 19.4], zoom_start=8)  # Alapértelmezett hely

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


def p_05_1_ugyfel_atadasa_05_2_nek(request, project_id, task_id):
    project = Project.objects.get(pk=project_id)
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
                # Felmérés rekord létrehozása ha még nem volt neki várakozó állapotú
                try:
                    Specify.objects.get(customer_project=task.customer_project, status='1:')
                except ObjectDoesNotExist:
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
                                    comment=f'{task.customer_project.customer} - ügyfelünkkel egyeztethetsz felmérést.\n'
                                            f'{form["reason"].value()}',
                                    created_project=project,
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_1_ugyfel_atadasa_05_2_nek.html', {'task': task, 'form': form})


################################# 05.2. #################################
def p_05_2_idopont_kereses(request, task_id):
    task = Task.objects.get(pk=task_id)

    today = timezone.now().date()
    specifys = (Specify.objects.filter(Q(status='1:') | Q(status='2:', specify_date__gte=today))
                       .order_by('specify_date'))

    p = Paginator(specifys, 10)
    page = request.GET.get('page', 1)
    specifys_page = p.get_page(page)
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
                    map_records = (Specify.objects.filter(status='2:',
                                                          specify_date__gte=start_date,
                                                          specify_date__lt=end_date))
                    for map_record in map_records:
                        # Készítünk egy Popup objektumot, amely tartalmazza a szükséges információkat
                        local_time = timezone.localtime(map_record.specify_date)
                        formatted_specify_date = local_time.strftime("%Y-%m-%d %H:%M")
                        popup_content = (f'{map_record.customer_project.customer} - {map_record.customer_project}<br>'
                                         f'{formatted_specify_date} - {map_record.specifier}')  # Újsor karakterrel választjuk el az adatokat
                        folium.Marker([map_record.customer_project.latitude,
                                       map_record.customer_project.longitude],
                                      popup=folium.Popup(popup_content, max_width=250),
                                      icon=folium.Icon(color='blue', icon='info-sign')).add_to(m1)

                    # Akiknek még nincs időpontjuk - térképre
                    map_records = Specify.objects.filter(status='1:')
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
                    # Visszalépés ide: p_05_2_ugyfel_egyeztetes_felmeresrol
                    return_view = getattr(app_views, 'view_names')  # Átalakítás, hogy hívható legyen
                    return return_view(request, view_name='p_05_2_ugyfel_egyeztetes_felmeresrol', task_id=task_id)
        else:
            initial_data = {'dateinput': datetime.now()}
            form = DateInputForm(initial=initial_data)

        return render(request, '05/p_05_2_idopont_kereses.html',
                      {'task': task, 'form': form, 'specifys': specifys_page, 'map': m1,
                       'page_list': specifys_page, 'page_range': page_range, })


def p_05_2_idopont_rogzites(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        specify = Specify.objects.get(status='1:', customer_project=task.customer_project)

        if request.method == 'POST':
            form = SpecifyDateTimeForm(request.POST or None, instance=specify)
            if form.is_valid():
                form.save()
                # Feladat átállítva Folyamatban értékre
                task.type = '3:'
                task.type_color = '3:'
                task.save()
                messages.success(request, 'Felmérési időpont rögzítve.')
                return render(request, 'home.html', {})
        else:
            form = SpecifyDateTimeForm(instance=specify)

        return render(request, '05/p_05_2_idopont_rogzites.html', {'task': task, 'form': form})


def p_05_2_felmero_rogzites(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        specify = Specify.objects.get(status='1:', customer_project=task.customer_project)

        if request.method == 'POST':
            form = SpecifierForm(request.POST or None, instance=specify)
            if form.is_valid():
                form.save()
                # Feladat átállítva Folyamatban értékre
                task.type = '3:'
                task.type_color = '3:'
                task.save()
                messages.success(request, 'Felmérő rögzítve.')
                return render(request, 'home.html', {})
        else:
            form = SpecifierForm(instance=specify)

        return render(request, '05/p_05_2_felmero_rogzites.html', {'task': task, 'form': form})


def p_05_2_ugyfel_atadasa_05_3_nak(request, project_id, task_id):
    project = Project.objects.get(pk=project_id)
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        # a feladathoz tartozó email sablon
        email_template_name = '05.2. Felmérési időpont küldése'
        email_template = EmailTemplate.objects.get(title=email_template_name)

        # szerkeszthető szöveg a sablon alapján
        template = Template(email_template.content)

        # az aktuális ügyfélnév, időpont és helyszín helyettesítése a sablon változója alapján
        specify = Specify.objects.get(status='1:', customer_project=task.customer_project)
        context = Context({'customer_name': task.customer_project.customer,
                           'specify_date': specify.specify_date,
                           'installation_address': task.customer_project.installation_address})
        rendered_content = template.render(context)

        if request.method == 'POST':
            form = EmailTemplateForm(request.POST, instance=email_template)
            if form.is_valid():
                subject = form['subject'].value()
                message = form['content'].value()
                to_email = [task.customer_project.customer.email]
                sent = send_mail(subject, message, DEFAULT_FROM_EMAIL, to_email, html_message=message)
                if sent:
                    # Az Új feladat jelzőből Elkészült jelző lesz
                    task.type = '4:'
                    task.type_color = '4:'
                    task.save()
                    specify.status = '2:'  # Egyeztetett felmérés lett
                    specify.email_sent_at = timezone.now()  # Email kiküldésének időpontja
                    specify.save()
                    messages.success(request, 'E-mail sikeresen elküldve.')
                    Task.objects.create(type='0:',  # Esemény bejegyzés
                                        type_color='0:',
                                        project=task.project,
                                        customer_project=task.customer_project,
                                        comment=f'{task.customer_project.customer} ügyfélnek - {email_template_name} - '
                                                f'nevű sablon email sikeresen kiküldve.',
                                        created_project=project,
                                        created_user=request.user)
                    # feladat átadása 05.3. Egyeztetett felméréseknek
                    next_project = Project.objects.filter(name__startswith='05.3.')
                    Task.objects.create(type='2:',  # Feladat típus
                                        type_color='2:',
                                        project=next_project[0],  # következő projekt
                                        customer_project=task.customer_project,  # ügyfél azonosító
                                        comment=f'{task.customer_project.customer} - ügyféllel egyeztetett felmérés:\n'
                                                f'Időpont: {specify.specify_date.strftime("%Y-%m-%d %H:%M")}\n'
                                                f'Felmérő: {specify.specifier}',
                                        created_project=project,
                                        created_user=request.user,
                                        deadline=specify.specify_date)
                    messages.success(request, f'{task.customer_project.customer} - továbbítva: '
                                              f'{next_project[0]} felé.')

                    # Email a felmérőnek is
                    email_template_name = '05.2. Felmérési időpont küldése a felmérőnek'
                    email_template = EmailTemplate.objects.get(title=email_template_name)

                    # szerkeszthető szöveg a sblon alapján
                    template = Template(email_template.content)

                    # az aktuális ügyfélnév, időpont és helyszín helyettesítése a sablon változója alapján
                    context = Context({'customer_name': task.customer_project.customer,
                                       'specify_date': specify.specify_date,
                                       'installation_address': task.customer_project.installation_address,
                                       'specifier_name': specify.specifier,
                                       'comment': specify.comment})
                    rendered_content = template.render(context)
                    subject = email_template.subject
                    message = rendered_content
                    to_email = [specify.specifier.email]
                    sent = send_mail(subject, message, DEFAULT_FROM_EMAIL, to_email, html_message=message)
                    if sent:
                        messages.success(request, f'{specify.specifier} felmérő is kapott emailt a felmérésről.')
                    else:
                        messages.success(request, 'Hiba történt a felmérő felé küldött e-mail küldése közben!')
                else:
                    Task.objects.create(type='1:',  # Figyelmeztető bejegyzés
                                        type_color='1:',
                                        project=task.project,
                                        customer_project=task.customer_project,
                                        comment=f'{task.customer_project.customer} ügyfélnek - {email_template_name} - '
                                            f'nevű sablon küldése nem sikerült.',
                                        created_project=project,
                                        created_user=request.user)
                    messages.success(request,'Hiba történt az ügyfél felé küldött e-mail küldése közben!')
                return render(request, 'home.html', {})
        else:
            form = EmailTemplateForm(instance=email_template, initial={'content': rendered_content})

        return render(request, '05/p_05_2_ugyfel_atadasa_05_3_nak.html',
                      {'task': task, 'form': form})


def p_05_2_ugyfel_atadasa_05_1_nek(request, project_id, task_id):
    project = Project.objects.get(pk=project_id)
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
                                    created_project=project,
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_2_ugyfel_atadasa_05_1_nek.html',
                      {'task': task, 'form': form})


################################# 05.3. #################################
def p_05_3_ugyfel_atadasa_05_4_nek(request, project_id, task_id):
    project = Project.objects.get(pk=project_id)
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                specify = Specify.objects.get(status='2:', customer_project=task.customer_project)
                specify.status = '4:'
                specify.save()

                # Eredeti task lezárása
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat visszaadása 05.1. Felmérése felelőséhez
                next_project = Project.objects.filter(name__startswith='05.4.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél azonosító
                                    comment=f'{task.customer_project.customer} -  ügyfelünk felmérését feldolgozhatod.\n'
                                            f'{form["reason"].value()}',
                                    created_project=project,
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_3_ugyfel_atadasa_05_4_nek.html',
                      {'task': task, 'form': form})

def p_05_3_ugyfel_atadasa_05_2_nek(request, project_id, task_id):
    task = Task.objects.get(pk=task_id)
    project = Project.objects.get(pk=project_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                specify = Specify.objects.get(status='2:', customer_project=task.customer_project)
                specify.status = '3:'
                specify.save()
                Specify.objects.create(customer_project=task.customer_project,
                                       status='1:',  # Várakozó felmérés
                                       created_user=request.user)
                # Eredeti task lezárása
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat visszaadása 05.1. Felmérése felelőséhez
                next_project = Project.objects.filter(name__startswith='05.2.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél azonosító
                                    comment=f'{task.customer_project.customer} -  ügyfelünkkel egyeztess új felmérést.\n'
                                            f'{form["reason"].value()}',
                                    created_project=project,
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_3_ugyfel_atadasa_05_2_nek.html',
                      {'task': task, 'form': form})


################################# 05.4. #################################
def p_05_4_felmeresi_kepek_feltoltese(request, task_id):
    task = Task.objects.get(pk=task_id)

    specifies = (Specify.objects.filter(status='4:', customer_project=task.customer_project).order_by('specify_date'))

    p = Paginator(specifies, 10)
    page = request.GET.get('page', 1)
    specifies_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    current_specify = ''

    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            action = request.POST.get('action')
            form = SpecifyPhotoForm(request.POST, request.FILES)
            if action:
                # Szétválasztjuk az egyedi azonosítót és a művelet nevét
                action_parts = action.split('_')
                action_name = action_parts[0]
                specify_id = action_parts[1]

                current_specify = Specify.objects.get(pk=specify_id)

                if action_name == 'date':
                    new_directory_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer_project.customer.id}',
                                                      'felmeresek', str(specify_id))
                    if not os.path.exists(new_directory_path):
                        # Ha nem létezik, hozzuk létre
                        os.makedirs(new_directory_path)
                elif action_name == 'upload':
                    files = request.FILES.getlist('photo')
                    specify = Specify.objects.get(pk=specify_id)
                    directory_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer_project.customer.id}',
                                                      'felmeresek', str(specify.id))
                    if files:
                        for file in files:
                            file_path = os.path.join(directory_path, file.name)
                            if not os.path.exists(file_path):  # Check if the file already exists
                                SpecifyPhoto.objects.create(specify=specify, photo=file)
                            else:
                                messages.success(request, f'Ez a kép ({file.name}) már fel volt töltve..')
                        messages.success(request, 'Sikeresen feltöltődtek az új fényképek.')
                        # Visszalépés ide: p_05_4_felmeresi_anyag_feldolgozasa
                        return_view = getattr(app_views, 'view_names')  # Átalakítás, hogy hívható legyen
                        return return_view(request, view_name='p_05_4_felmeresi_anyag_feldolgozasa', task_id=task_id)
        else:
            form = SpecifyPhotoForm()

        return render(request, '05/p_05_4_felmeresi_kepek_feltoltese.html',
                      {'task': task, 'specifies': specifies_page,
                       'page_list': specifies_page, 'page_range': page_range,
                       'current_specify': current_specify, 'form': form})


def p_05_4_felmeresi_kepek_csoportositasa(request, task_id):
    task = Task.objects.get(pk=task_id)

    specifies = (Specify.objects.filter(status='4:', customer_project=task.customer_project).order_by('specify_date'))

    p = Paginator(specifies, 10)
    page = request.GET.get('page', 1)
    specifies_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    current_specify = ''
    specify_photos = ''

    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            action = request.POST.get('action')
            if action:
                # Szétválasztjuk az egyedi azonosítót és a művelet nevét
                action_parts = action.split('_')
                action_name = action_parts[0]
                specify_id = action_parts[1]

                if action_name == 'date':
                    return redirect('p_05_4_felmeresi_kep_kivalasztasa', task_id=task_id, specify_id=specify_id)
                elif action_name == 'back':
                    # Visszalépés ide: p_05_4_felmeresi_anyag_feldolgozasa
                    return_view = getattr(app_views, 'view_names')  # Átalakítás, hogy hívható legyen
                    return return_view(request, view_name='p_05_4_felmeresi_anyag_feldolgozasa', task_id=task_id)

        return render(request, '05/p_05_4_felmeresi_kepek_csoportositasa.html',
                      {'task': task, 'specifies': specifies_page,
                       'page_list': specifies_page, 'page_range': page_range,})


def p_05_4_felmeresi_kep_kivalasztasa(request, task_id, specify_id):
    task = Task.objects.get(pk=task_id)
    current_specify = Specify.objects.get(pk=specify_id)
    specify_photos = SpecifyPhoto.objects.filter(specify=specify_id).order_by('photo')

    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            action = request.POST.get('action')
            if action:
                # Szétválasztjuk az egyedi azonosítót és a művelet nevét
                action_parts = action.split('_')
                action_name = action_parts[0]
                specify_or_photo_id = action_parts[1]

                if action_name == 'photo':
                    return redirect('p_05_4_felmeresi_kepek_tipusai', task_id=task_id,
                                    specify_id=specify_id, photo_id=specify_or_photo_id)
                elif action_name == 'back':
                    return redirect('p_05_4_felmeresi_kepek_csoportositasa', task_id=task_id)

        return render(request, '05/p_05_4_felmeresi_kep_kivalasztasa.html',
                      {'task': task, 'current_specify': current_specify, 'specify_photos': specify_photos})


def p_05_4_felmeresi_kepek_tipusai(request, task_id, specify_id, photo_id):
    task = Task.objects.get(pk=task_id)
    specify_photo = SpecifyPhoto.objects.get(pk=photo_id)

    if request.method == 'POST':
        form_type = SpecifyPhotoTypeForm(request.POST, request.FILES, instance=specify_photo)
        # form_type = ReasonForm(request.POST)
        if form_type.is_valid():
            form_type.save()
            return redirect('p_05_4_felmeresi_kep_kivalasztasa', task_id=task_id, specify_id=specify_id)
    else:
        form_type = SpecifyPhotoTypeForm(instance=specify_photo)
        # form_type = ReasonForm()

    return render(request, '05/p_05_4_felmeresi_kepek_tipusai.html',
                  {'task': task, 'specify_photo': specify_photo,
                   'form_type': form_type})


def p_05_4_uj_felmeres_feladat_05_2_nek(request, project_id, task_id):
    project = Project.objects.get(pk=project_id)
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = ReasonForm(request.POST)
            if form.is_valid():
                Specify.objects.create(customer_project=task.customer_project,
                                       status='1:',  # Várakozó felmérés
                                       created_user=request.user)
                # Eredeti task lezárása
                task.type = '3:'
                task.type_color = '3:'
                task.save()

                # új feladat 05.2. Ügyfél egyeztetés felmérésnek
                next_project = Project.objects.filter(name__startswith='05.2.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer_project=task.customer_project,  # ügyfél azonosító
                                    comment=f'{task.customer_project.customer} - Új felmérés szükséges.\n'
                                            f'{form["reason"].value()}',
                                    created_project=project,
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_4_uj_felmeres_feladat_05_2_nek.html', {'task': task, 'form': form})


################################# 05.x. #################################
def p_05_x_ugyfel_atadasa_02_1_nek(request, project_id, task_id):
    project = Project.objects.get(pk=project_id)
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
                task.type = '5:'
                task.type_color = '5:'
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
                                    created_project=project,
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_x_ugyfel_atadasa_02_1_nek.html', {'task': task, 'form': form})


def p_05_x_ugyfel_atadasa_04_1_nek(request, project_id, task_id):
    project = Project.objects.get(pk=project_id)
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
                task.type = '5:'
                task.type_color = '5:'
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
                                    created_project=project,
                                    created_user=request.user)
                messages.success(request, f'{task.customer_project.customer} - továbbítva: {next_project[0]} felé.')
                return render(request, 'home.html', {})
        else:
            form = ReasonForm()

        return render(request, '05/p_05_x_ugyfel_atadasa_04_1_nek.html', {'task': task, 'form': form})


def specifies(request, status):
    specifies = Specify.objects.filter(status=status).select_related(
        'customer_project__customer',
        'customer_project__target',
        'customer_project__financing',
        'specifier'
    ).order_by('-specify_date')

    p = Paginator(specifies, 10)
    page = request.GET.get('page', 1)
    specifies_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    if status == '1:':
        fejlec = 'Várakozó'
    elif status == '2:':
        fejlec = 'Egyeztetett'
    elif status == '3:':
        fejlec = 'Elmaradt'
    elif status == '4:':
        fejlec = 'Megtörtént'

    m1 = folium.Map(location=[47.2, 19.4], zoom_start=7)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            # Szétválasztjuk az egyedi azonosítót és a művelet nevét
            action_parts = action.split('_')
            action_name = action_parts[0]
            specify_day = action_parts[1]

            # Kezdő dátum és vég dátum meghatározása
            map_day = datetime.strptime(specify_day, '%Y-%m-%d').date()
            start_date = timezone.make_aware(datetime.combine(map_day, datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(map_day + timedelta(days=1), datetime.min.time()))

            map_records = (Specify.objects.filter(status=status,
                                                  specify_date__gte=start_date,
                                                  specify_date__lt=end_date))
            for map_record in map_records:
                # Készítünk egy Popup objektumot, amely tartalmazza a szükséges információkat
                local_time = timezone.localtime(map_record.specify_date)
                formatted_specify_date = local_time.strftime("%Y-%m-%d %H:%M")
                popup_content = (f'{map_record.customer_project.customer} - {map_record.customer_project}<br>'
                                 f'{formatted_specify_date} - {map_record.specifier}')  # Újsor karakterrel választjuk el az adatokat
                folium.Marker([map_record.customer_project.latitude,
                               map_record.customer_project.longitude],
                              popup=folium.Popup(popup_content, max_width=250),
                              icon=folium.Icon(color='blue', icon='info-sign')).add_to(m1)
            m1 = m1._repr_html_()  # HTML-reprezentáció
    else:
        specify_day = ''
        if status == '1:':
            map_records = (Specify.objects.filter(status=status))
            for map_record in map_records:
                # Készítünk egy Popup objektumot, amely tartalmazza a szükséges információkat
                popup_content = (f'{map_record.customer_project.customer} - {map_record.customer_project}<br>'
                                 f' - {map_record.specifier}')  # Újsor karakterrel választjuk el az adatokat
                folium.Marker([map_record.customer_project.latitude,
                               map_record.customer_project.longitude],
                              popup=folium.Popup(popup_content, max_width=250),
                              icon=folium.Icon(color='blue', icon='info-sign')).add_to(m1)
        m1 = m1._repr_html_()  # HTML-reprezentáció

    return render(request, 'specifies.html', {'specifies': specifies_page,
                                              'page_list': specifies_page, 'page_range': page_range,
                                              'fejlec': fejlec, 'map': m1, 'specify_day': specify_day})