from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from . import views_projects as app_views

from .context_processors import menu_context
from .forms_projects import DeadlineForm

from .models import Project, Task, Job, Customer, CustomerProject, LastPosition


def home(request):
    return render(request, 'home.html', {})


# Projekt név átvétele az url-ből, majd a Project-ben az ahhoz tartozó view_name definíció hívása
def view_names(request, view_name, task_id):
    job = LastPosition.objects.get(user=request.user)
    project = get_object_or_404(Project, view_name=view_name)  # Projekt rekord keresése a view név alapján

    # Van-e ilyen pozicíója a felhasználónak?
    is_assigned = job.last_position.positionproject_set.filter(project=project).exists()
    if not is_assigned:
        messages.success(request, 'Ehhez a munkakörhöz nincs jogosultságod. Jelezd az adminisztrátornak!')
        return render(request, 'home.html', {})

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


def hatarido(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = DeadlineForm(request.POST or None, instance=task)
            if form.is_valid():
                form.save()
                # Feladat átállítva Folyamatban értékre
                task.type = '3:'
                task.type_color = '3:'
                task.save()
                messages.success(request, 'Határidő módosítva.')
                return render(request, 'home.html', {})
        else:
            form = DeadlineForm(instance=task)

        return render(request, 'hatarido.html', {'task': task, 'form': form})


# Feladatok listázása különféle szűrőkkel
def deadline_tasks(request):
    if request.user.is_authenticated:
        tasks_set = (Task.objects.filter(project__in=menu_context(request)['position_projects'])
                     .filter(deadline__isnull=False)
                     .filter(Q(type='2:') | Q(type='3:'))
                     .order_by('deadline'))
        type_choices = Task.TYPE_CHOICES
        type_color = Task.COLOR_CHOICES

        p = Paginator(tasks_set, 10)
        page = request.GET.get('page', 1)
        tasks_page = p.get_page(page)
        page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

        return render(request, 'deadline_tasks.html', {'tasks': tasks_page,
                                              'page_list': tasks_page, 'page_range': page_range,
                                              'type_choices': type_choices, 'type_color': type_color})
    else:
        messages.success(request, 'Nincs jogosultságod.')
        return redirect('login')


# keresés eredménye a CustomerProject és Customer tábla szűrésével
def customers(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Névben, címben és telefonszámban is keresünk
            searched = request.POST['searched']
            if searched == '':
                messages.success(request, 'Üres a Keresés mező.')
                return render(request, 'home.html', {})
            else:
                words = searched.split()  # Felbontjuk a keresési szavakat
                q_objects = Q()  # Üres Q objektum létrehozása

                # Minden szóra létrehozunk egy Q objektumot, és azokat az | operátorral összekapcsoljuk
                for word in words:
                    q_objects |= Q(customer__surname__icontains=word)
                    q_objects |= Q(customer__name__icontains=word)
                    q_objects |= Q(customer__email__icontains=word)
                    q_objects |= Q(customer__phone__icontains=word)
                    q_objects |= Q(customer__address__icontains=word)
                    q_objects |= Q(installation_address__icontains=word)

                customer_project_set = (CustomerProject.objects.filter(q_objects)
                                        .distinct().order_by('customer__surname', 'customer__name'))

        p = Paginator(customer_project_set, 10)
        page = request.GET.get('page', 1)
        customer_project_page = p.get_page(page)
        page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

        return render(request, 'customers_projects.html', {'customers_projects': customer_project_page,
                                              'page_list': customer_project_page, 'page_range': page_range,
                                              'searched': searched})
    else:
        messages.success(request, 'Nincs jogosultságod.')
        return redirect('login')


# Customer történet
def customer_history(request, customer_project_id):
    if request.user.is_authenticated:
        tasks_set = Task.objects.filter(customer_project=customer_project_id).order_by('-created_at')

        customer_project = CustomerProject.objects.get(pk=customer_project_id)
        customer = customer_project.customer

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
