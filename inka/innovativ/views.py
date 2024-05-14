from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from collections import defaultdict
from . import views_projects as app_views

from .context_processors import menu_context

from .models import Project, Task, Job, Customer


def home(request):
    return render(request, 'home.html', {})


# Projekt név átvétele az url-ből, majd a Project-ben az ahhoz tartozó view_name definíció hívása
def view_names(request, view_name, task_id):
    job = Job.objects.get(user=request.user)
    project = get_object_or_404(Project, view_name=view_name)  # Projekt rekord keresése a view név alapján

    # Van-e ilyen pozicíója a felhasználónak?
    is_assigned = job.position.positionproject_set.filter(project=project).exists()
    if not is_assigned:
        messages.success(request, 'Ehhez a munkakörhöz nincs jogosultságod. Jelezd az adminisztrátornak!')
        return render(request, 'home.html', {})

    # view_name = project.view_name  # A rekordban a meghívandó view neve

    if hasattr(app_views, view_name):  # Ha van ilyen view a views_projects.py file-ban
        desired_view = getattr(app_views, view_name)  # Átalakítás, hogy hívható legyen
        return desired_view(request, project, task_id)
    else:
        messages.success(request, 'Hiba történt, nincs ilyen nézet a rendszerben. Jelezd az adminisztrátornak!')
        return render(request, 'home.html', {})


# Feladatok listázása különféle szűrőkkel
def tasks(request, filter, view_name):
    if request.user.is_authenticated:
        if view_name == 'all':
            project_name = 'all'
            if filter == 'new':
                tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                                type='2:').order_by('-created_at')
            elif filter == 'in_progress':
                tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                                type='3:').order_by('-created_at')
            elif filter == 'ready':
                tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                                type='4:').order_by('-created_at')
            elif filter == 'closed':
                tasks_set = Task.objects.filter(project__in=menu_context(request)['position_projects'],
                                                type='5:').order_by('-created_at')
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
            project = get_object_or_404(Project, view_name=view_name)
            project_name = project
            if filter == 'new':
                tasks_set = Task.objects.filter(project=project,
                                                type='2:').order_by('-created_at')
            elif filter == 'in_progress':
                tasks_set = Task.objects.filter(project=project,
                                                type='3:').order_by('-created_at')
            elif filter == 'ready':
                tasks_set = Task.objects.filter(project=project,
                                                type='4:').order_by('-created_at')
            elif filter == 'closed':
                tasks_set = Task.objects.filter(project=project,
                                                type='5:').order_by('-created_at')
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

        return render(request, 'tasks.html', {'tasks': tasks_page,
                                              'page_list': tasks_page, 'page_range': page_range,
                                              'type_choices': type_choices, 'type_color': type_color,
                                              'project_name': project_name, 'view_name': view_name})
    else:
        messages.success(request, 'Nincs jogosultságod.')
        return redirect('login')


# keresés eredménye a Customer tábla szűrésével
def customers(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Névben, címben és telefonszámban is keresünk
            searched = request.POST['searched']
            if searched == '':
                messages.success(request, 'Üres a Keresés mező.')
                return render(request, 'home.html', {})
            else:
                customer_set = (Customer.objects.filter(
                    Q(surname__icontains=searched) |
                    Q(name__icontains=searched) |
                    Q(email__icontains=searched) |
                    Q(phone__icontains=searched) |
                    Q(address__icontains=searched) |
                    Q(installation_address__icontains=searched))
                                .order_by('surname', 'name'))

        p = Paginator(customer_set, 10)
        page = request.GET.get('page', 1)
        customer_page = p.get_page(page)
        page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

        return render(request, 'customers.html', {'customers': customer_page,
                                              'page_list': customer_page, 'page_range': page_range,
                                              'searched': searched})
    else:
        messages.success(request, 'Nincs jogosultságod.')
        return redirect('login')


# Customer történet
def customer_history(request, customer_id):
    if request.user.is_authenticated:
        tasks_set = Task.objects.filter(customer=customer_id).order_by('-created_at')

        customer = Customer.objects.get(pk=customer_id)

        type_choices = Task.TYPE_CHOICES
        type_color = Task.COLOR_CHOICES

        p = Paginator(tasks_set, 10)
        page = request.GET.get('page', 1)
        tasks_page = p.get_page(page)
        page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

        return render(request, 'customer_history.html', {'tasks': tasks_page,
                                             'type_choices': type_choices, 'type_color': type_color,
                                             'page_list': tasks_page, 'page_range': page_range,
                                             'task': tasks_set[0], 'customer': customer,})
    else:
        messages.success(request, 'Nincs jogosultságod.')
        return redirect('login')


# def projects(request):
#     # Projektekhez tartozó feladatok kigyűjtése
#     task_set = Task.objects.filter(project__in=menu_context(request)['position_projects'])
#
#     projects_tasks = defaultdict(list)  # üres szótár
#
#     # Csoportosítjuk a feladatokat a projektek szerint
#     for task in task_set:
#         projects_tasks[task.project.name].append(task)  # Projektekhez tartozó feladatok csoportosítva
#
#     projects_tasks = dict(projects_tasks)  # átalakítás szótárra
#
#     projects_tasks_list = [(project, tasks) for project, tasks in projects_tasks.items()]
#
#     p = Paginator(projects_tasks_list, 2)
#     page = request.GET.get('page', 1)
#     projects_tasks_page = p.get_page(page)
#     page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)
#
#     return render(request, 'projects_tasks.html', {'projects_tasks': projects_tasks_page,
#                                              'page_list': projects_tasks_page, 'page_range': page_range})


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

