# Ez arra jó, hogy minden sablonhoz hozzáadja ezt a context-et is
# Persze a settings.py.ben is be kell ezt a modult.
from django.contrib import messages

from .models import Job, Position, PositionProject


def menu_context(request):
    if request.user.is_authenticated:
        job = Job.objects.get(user=request.user)
        position = Position.objects.get(pk=job.position.id)
        projects = PositionProject.objects.filter(position=job.position)
        if not projects:
            messages.success(request, 'Ehhez a munkakörhöz még nincs rendelve egyetlen projekt sem. '
                                      'Jelezd az adminisztrátornak!')
        return {'position': position, 'projects': projects}

    else:
        return {'position': '', 'projects': ''}
