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
def project_names(request, project_name):
    project = get_object_or_404(Project, name=project_name)  # Projekt rekord keresése a projekt név alapján
    view_name = project.view_name  # A rekordban a meghívandó view neve

    if hasattr(app_views, view_name):  # Ha van ilyen view a views_projects.py file-ban
        desired_view = getattr(app_views, view_name)  # Átalakítás, hogy hívható legyen
        return desired_view(request, project_name)
    else:
        messages.success(request, 'Hiba történt, nincs ilyen nézet a rendszerben. Jelezd az adminisztrátornak!')
        return render(request, 'home.html', {})


def tasks(request):
    # Projektekhez tartozó feladatok kigyűjtése
    tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects']).order_by('-created_at')

    p = Paginator(tasks_set, 2)
    page = request.GET.get('page', 1)
    tasks_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    return render(request, 'tasks.html', {'tasks': tasks_page, 'page_range': page_range})


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

