# Ez arra jó, hogy minden sablonhoz hozzáadja ezt a context-et is
# Persze a settings.py.ben is be kell ezt a modult.

from .models import Job


def position(request):
    position = None
    if request.user.is_authenticated:
        position = Job.objects.get(user=request.user)
    return {'position': position}
