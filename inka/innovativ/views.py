from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from . import views_projects as app_views
from .models import Project


def home(request):
    return render(request, 'home.html', {})


# Projekt név átvétele az url-ből
def projects(request, project_name):
    project = get_object_or_404(Project, name=project_name)  # Projekt rekord keresése a projekt név alapján
    view_name = project.view_name  # A rekordban a meghívandó view neve

    if hasattr(app_views, view_name):  # ha van ilyen view a views_projects.py file-ban
        desired_view = getattr(app_views, view_name)  # átalakítás, hogy hívható legyen
        return desired_view(request)
    else:
        messages.success(request, 'Hiba történt, nincs ilyen nézet a rendszerben. Jelezd az adminisztrátornak!')
        return render(request, 'home.html', {})
