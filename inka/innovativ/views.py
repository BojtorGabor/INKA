from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from . import views_projects as app_views
from .context_processors import menu_context
from .models import Project, Task, Job, Position, PositionProject


def home(request):
    return render(request, 'home.html', {})


# Projekt név átvétele az url-ből, majd a Project-ben az ahhoz tartozó view_name definíció hívása
def project_names(request, project_name):
    project = get_object_or_404(Project, name=project_name)  # Projekt rekord keresése a projekt név alapján
    view_name = project.view_name  # A rekordban a meghívandó view neve

    if hasattr(app_views, view_name):  # Ha van ilyen view a views_projects.py file-ban
        desired_view = getattr(app_views, view_name)  # Átalakítás, hogy hívható legyen
        return desired_view(request)
    else:
        messages.success(request, 'Hiba történt, nincs ilyen nézet a rendszerben. Jelezd az adminisztrátornak!')
        return render(request, 'home.html', {})


def projects(request):
    # Projektekhez tartozó feladatok kigyűjtése
    task_set = Task.objects.filter(project__in=menu_context(request)['position_projects'])

    project_tasks = defaultdict(list)  # üres szótár

    # Csoportosítjuk a feladatokat a projektek szerint
    for task in task_set:
        project_tasks[task.project.name].append(task)  # Projektekhez tartozó feladatok csoportosítva

    project_tasks = dict(project_tasks)  # átalakítás szótárra

    return render(request, 'projects.html', {'project_tasks': project_tasks})


'''A tasks egy listája a Task model objektumoknak, amelyeket korábban kigyűjtöttél az adott felhasználóhoz 
    tartozó projektek alapján. A cél az, hogy ezeket a feladatokat csoportosítsuk a projektek szerint.
    
    A project_tasks egy defaultdict, ami azt jelenti, hogy alapértelmezett értéket rendel hozzá minden kulcshoz, 
    ha a kulcs még nem létezik. Ebben az esetben a list típust használjuk alapértelmezett értékként, ami egy üres 
    lista.
    
    A for task in tasks: ciklus minden task objektumon végigmegy a tasks listában. A task.project.name azt 
    jelenti, hogy a task objektumhoz tartozó projekt nevét kérjük le.
    
    A task.project a Task model egy olyan mezője, amely egy ForeignKey a Project modelre. A .name pedig a projekt
    modell name mezőjére hivatkozik.
    
    Az append(task) hozzáfűzi a task objektumot a project_tasks dictionaryben a megfelelő kulcshoz.
    A kulcs a projekt neve, amelyhez a feladat tartozik. Tehát minden egyes feladatot hozzáadjuk a megfelelő projekt
    nevével indexelt listához a project_tasks dictionary-ben.
    
    Így tehát a ciklus végrehajtásának eredményeképpen a project_tasks dictionaryben minden kulcshoz tartozik egy lista,
    amely tartalmazza az adott projekthez rendelt feladatokat. Ez a módszer csoportosítja a feladatokat a projektek
    szerint a dictionaryben.'''

