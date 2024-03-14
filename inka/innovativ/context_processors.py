# Ez arra jó, hogy minden sablonhoz hozzáadja ezt a context-et is
# Persze a settings.py.ben is be kell ezt a modult.
from django.utils import timezone
from django.contrib import messages
from .models import Job, Position, PositionProject


def menu_context(request):
    now = timezone.now()
    current_year = now.year

    if request.user.is_authenticated:
        job = Job.objects.get(user=request.user)  # Felhasználó munkaköre
        position = Position.objects.get(pk=job.position.id)  # Munkakör megnevezése
        position_projects = PositionProject.objects.filter(position=job.position)  # Munkakörhöz tartozó projektek
        if not position_projects:
            messages.success(request, 'Ehhez a munkakörhöz még nincs rendelve egyetlen projekt sem. '
                                      'Jelezd az adminisztrátornak!')
        else:
            return {'current_year': current_year, 'position': position, 'position_projects': position_projects}

    else:
        return {'current_year': current_year, 'position': '', 'projects': ''}
