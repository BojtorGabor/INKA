import csv
import os

from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from collections import defaultdict
from . import views_projects as app_views

from .context_processors import menu_context

from .models import Project, Task


def home(request):
    return render(request, 'home.html', {})


# Projekt név átvétele az url-ből, majd a Project-ben az ahhoz tartozó view_name definíció hívása
def project_names(request, project_name, filter):
    project = get_object_or_404(Project, name=project_name)  # Projekt rekord keresése a projekt név alapján
    view_name = project.view_name  # A rekordban a meghívandó view neve

    if hasattr(app_views, view_name):  # Ha van ilyen view a views_projects.py file-ban
        desired_view = getattr(app_views, view_name)  # Átalakítás, hogy hívható legyen
        return desired_view(request, project, filter)
    else:
        messages.success(request, 'Hiba történt, nincs ilyen nézet a rendszerben. Jelezd az adminisztrátornak!')
        return render(request, 'home.html', {})
#
#
# def tasks_old(request, filter):
#     # Projektekhez tartozó feladatok kigyűjtése
#     if filter == 'new':
#         tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
#                                         type='2:').order_by('-created_at')
#     elif filter == 'in_progress':
#         tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
#                                         type='3:').order_by('-created_at')
#     elif filter == 'ready':
#         tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
#                                         type='4:').order_by('-created_at')
#     elif filter == 'warning':
#         tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
#                                         type='1:').order_by('-created_at')
#     elif filter == 'event':
#         tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
#                                         type='0:').order_by('-created_at')
#     elif filter == 'all':
#         tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects']
#                                         ).order_by('-created_at')
#     type_choices = Task.TYPE_CHOICES
#     type_color = Task.COLOR_CHOICES
#
#     p = Paginator(tasks_set, 10)
#     page = request.GET.get('page', 1)
#     tasks_page = p.get_page(page)
#     page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)
#
#     return render(request, 'tasks.html', {'tasks': tasks_page, 'type_choices': type_choices,
#                                           'type_color': type_color, 'page_range': page_range})


def tasks(request, filter, project_name):
    if project_name == 'all':
        if filter == 'new':
            tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                            type='2:').order_by('-created_at')
        elif filter == 'in_progress':
            tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                            type='3:').order_by('-created_at')
        elif filter == 'ready':
            tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                            type='4:').order_by('-created_at')
        elif filter == 'warning':
            tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                            type='1:').order_by('-created_at')
        elif filter == 'event':
            tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                            type='0:').order_by('-created_at')
        elif filter == 'all':
            tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects']
                                            ).order_by('-created_at')
    else:
        project = get_object_or_404(Project, name=project_name)
        if filter == 'new':
            tasks_set = Task.objects.filter(project=project,
                                            type='2:').order_by('-created_at')
        elif filter == 'in_progress':
            tasks_set = Task.objects.filter(project=project,
                                            type='3:').order_by('-created_at')
        elif filter == 'ready':
            tasks_set = Task.objects.filter(project=project,
                                            type='4:').order_by('-created_at')
        elif filter == 'warning':
            tasks_set = Task.objects.filter(project=project,
                                            type='1:').order_by('-created_at')
        elif filter == 'event':
            tasks_set = Task.objects.filter(project=project,
                                            type='0:').order_by('-created_at')
        elif filter == 'all':
            tasks_set = Task.objects.filter(project=project
                                            ).order_by('-created_at')
    type_choices = Task.TYPE_CHOICES
    type_color = Task.COLOR_CHOICES

    p = Paginator(tasks_set, 10)
    page = request.GET.get('page', 1)
    tasks_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    return render(request, 'tasks.html', {'tasks': tasks_page, 'type_choices': type_choices,
                                          'type_color': type_color, 'page_range': page_range})

from .forms_projects import CSVFileSelectForm
from .models import Customer, Task, Project


def p_01_1_ugyfel_adat_import(request, project, filter):  # Új ügyfelek importálása
    if request.method == 'POST':
        form = CSVFileSelectForm(request.POST, request.FILES)  # Import fájl kiválasztása
        if form.is_valid():
            file_name = request.FILES['file'].name
            file_path = os.path.join(settings.BASE_DIR, 'import')
            file_path = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):  # Csak és kizárólag az inka/import/ könyvtárból fogad el import fájlt
                messages.success(request, 'Az import könytárban nem találtam a kiválasztott fájlt!')
            else:
                if p_01_1_ugyfel_adat_import_items(request, file_path, project):  # import fájl feldolgozás
                    return render(request, 'home.html', {})  # sikeres
                else:
                    render(request, 'p_01_1_ugyfel_adat_import.html',
                           {'project': project, 'form': form})  # sikertelen, adatszerkezet hiba?
    else:
        form = CSVFileSelectForm()
    return render(request, 'p_01_1_ugyfel_adat_import.html', {'project': project, 'form': form})


def p_01_1_ugyfel_adat_import_items(request, file_path, project):  # Import fájl ellenőrzés és adatbedolgozás
    with open(file_path, 'r', encoding='utf-8') as csv_file:  # a kiválasztott csv file
        csv_reader = csv.reader(csv_file, delimiter=';')  # pontosvesszővel elválasztva
        for row_number, row in enumerate(csv_reader, start=1):  # jelenleg 6 tételt várok
            if len(row) < 6:
                messages.success(request, f'Az import fájlban ({file_path})'
                                          f' nincs elegendő adat a {row_number}. sorban!')
                messages.success(request, 'FIGYELEM! A fájlban található összes adat nem került beolvasásra!')
                return False
        # csv_file.seek(0)
        # total_rows = sum(1 for row in csv_reader)

        csv_file.seek(0)  # fájl kurzor előre állítása

        next_project = Project.objects.filter(name__startswith='02.1.')  # feladat adás a következő projektnek
        existing_emails = ''  # email ellenőrzéshez, ebben lesz felsorolva ha már volt ilyen email
        new_customer_number = 0
        for row_number, row in enumerate(csv_reader, start=1):  # csv sorokon végigfut
            surname, name, email, phone, address, rooftop = row  # szétbontja a sort
            existing_customer = Customer.objects.filter(email=email)  # email keresés
            if existing_customer.exists():  # már volt ilyen a customer táblában,
                existing_emails = existing_emails + ' -> ' + email  # kigyűjti ezeket az emaileket
            else:  # tényleg új ügyfél
                new_customer_number += 1
                new_customer = Customer.objects.create(surname= surname,
                                                       name= name,
                                                       email= email,
                                                       phone=phone,
                                                       address=address,
                                                       rooftop=rooftop)  # ügyfél felvétele a customer táblába
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer= new_customer,  # ügyfél azonosító
                                    comment=f'Új ügyfelünket: {new_customer} keresd fel adategyeztetés céljából!',
                                    created_user=request.user)
        if existing_emails:  # volt ismétlődő email
            Task.objects.create(type='1:',  # Figyelmeztető bejegyzésés
                                type_color='1:',
                                project=project,
                                comment=f'{file_path}\nfájl importálása során a következő email címek duplikálás miatt '
                                        f'nem kerültek be az ügyfél táblába:\n\n{existing_emails}',
                                created_user=request.user)
            messages.success(request, 'Az importálás csak részben sikeres, voltak duplikált email címek. '
                                      'Ezeket az email címeket megtalálod a Figyelmeztés sorban. ')
        else:
            Task.objects.create(type='0:',  # Sima esemény bejegyzés
                                type_color='0:',
                                project=project,
                                comment=f'{file_path}\n'
                                        f'Össszesen: {new_customer_number} új ügyfél importálása megtörtént.',
                                created_user=request.user)
            messages.success(request, 'Sikeres importálás.')
    return True



def projects(request):
    # Projektekhez tartozó feladatok kigyűjtése
    task_set = Task.objects.filter(project__in=menu_context(request)['position_projects'])

    projects_tasks = defaultdict(list)  # üres szótár

    # Csoportosítjuk a feladatokat a projektek szerint
    for task in task_set:
        projects_tasks[task.project.name].append(task)  # Projektekhez tartozó feladatok csoportosítva

    projects_tasks = dict(projects_tasks)  # átalakítás szótárra

    projects_tasks_list = [(project, tasks) for project, tasks in projects_tasks.items()]

    p = Paginator(projects_tasks_list, 2)
    page = request.GET.get('page', 1)
    projects_tasks_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    return render(request, 'projects_tasks.html', {'projects_tasks': projects_tasks_page,
                                             'page_range': page_range})


'''A tasks egy listája a Task model objektumoknak, amelyeket korábban kigyűjtöttél az adott felhasználóhoz 
    tartozó projektek alapján. A cél az, hogy ezeket a feladatokat csoportosítsuk a projektek szerint.
    
    A projects_tasks egy defaultdict, ami azt jelenti, hogy alapértelmezett értéket rendel hozzá minden kulcshoz, 
    ha a kulcs még nem létezik. Ebben az esetben a list típust használjuk alapértelmezett értékként, ami egy üres 
    lista.
    
    A for task in tasks: ciklus minden task objektumon végigmegy a tasks listában. A task.project.name azt 
    jelenti, hogy a task objektumhoz tartozó projekt nevét kérjük le.
    
    A task.project a Task model egy olyan mezője, amely egy ForeignKey a Project modelre. A .name pedig a projekt
    modell name mezőjére hivatkozik.
    
    Az append(task) hozzáfűzi a task objektumot a projects_tasks dictionaryben a megfelelő kulcshoz.
    A kulcs a projekt neve, amelyhez a feladat tartozik. Tehát minden egyes feladatot hozzáadjuk a megfelelő projekt
    nevével indexelt listához a project_tasks dictionary-ben.
    
    Így tehát a ciklus végrehajtásának eredményeképpen a projects_tasks dictionaryben minden kulcshoz tartozik egy lista,
    amely tartalmazza az adott projekthez rendelt feladatokat. Ez a módszer csoportosítja a feladatokat a projektek
    szerint a dictionaryben.'''

