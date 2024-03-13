from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import Job, Position, Project


def home(request):
    # Aktuális év
    now = timezone.now()
    current_year = now.year

    if request.user.is_authenticated:
        position = Job.objects.get(user=request.user)
        pos = Position.objects.get(pk=position.id)
        projects = pos.positionproject_set.all()
    else:
        position = ''
        projects = ''
    return render(request, 'home.html', {'current_year': current_year, 'position': position,
                                         'projects': projects})


def projects(request, text):
    cont = get_object_or_404(Project, name=text)
    return render(request, 'projects.html', {'cont': cont})