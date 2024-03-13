from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import Job, Position, Project, PositionProject


def home(request):
    # Aktuális év
    now = timezone.now()
    current_year = now.year

    # if request.user.is_authenticated:
        # menu_data =get_menu(request)
        # position = menu_data['position']
        # projects = menu_data['projects']

        # if not projects:
        #     messages.success(request, 'Ehhez a munkakörhöz még nincs rendelve egyetlen projekt sem. '
        #                               'Jelezd az adminisztrátornak!')
    # else:
    #     position = ''
    #     projects = ''
    return render(request, 'home.html', {'current_year': current_year,})


def projects(request, text):
    cont = get_object_or_404(Project, name=text)

    # menu_data = get_menu(request)
    # position = menu_data['position']
    # projects = menu_data['projects']

    return render(request, 'projects.html', {'cont': cont})


def get_menu(request):
    job = Job.objects.get(user=request.user)
    position = Position.objects.get(pk=job.position.id)
    projects = PositionProject.objects.filter(position=job.position)
    return {'position': position, 'projects': projects}
