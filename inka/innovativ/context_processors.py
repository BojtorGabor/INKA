# Ez arra jó, hogy minden sablonhoz hozzáadja ezt a context-et is
# Persze a settings.py.ben is be kell ezt a modult.
from django.utils import timezone
from django.contrib import messages
from .models import Job, Position, PositionProject, LastPosition


def menu_context(request):
    now = timezone.now()
    current_year = now.year

    if request.user.is_authenticated:
        last_position = LastPosition.objects.get(user=request.user).last_position  # Felhasználó munkaköre
        all_positions = Position.objects.filter(job__user=request.user).order_by('name')  # Felhasználó lehetságes munkakörei
        possible_positions = [{'id': pp.id, 'name': pp.name} for pp in all_positions]  # Átalakítás listává

        if last_position:
            position_projects = PositionProject.objects.filter(position=last_position)  # Munkakörhöz tartozó projektek
            projects = [pp.project for pp in position_projects]  # Átalakítás listává
            return {'current_year': current_year, 'position': str(last_position),
                    'possible_positions': possible_positions, 'position_projects': projects}
        else:
            messages.success(request, 'Ehhez a munkakörhöz még nincs rendelve egyetlen projekt sem. '
                                      'Jelezd az adminisztrátornak!')
        return {'current_year': current_year, 'position': '', 'last_position': '',
                'possible_positions': '', 'position_projects': []}
    else:
        return {'current_year': current_year, 'position': '', 'last_position': '',
                'possible_positions': '', 'position_projects': []}
    #
    #
    # if request.user.is_authenticated:
    #     job = Job.objects.filter(user=request.user)  # Felhasználó munkaköre
    #     if len(job) == 1:
    #         job = Job.objects.get(user=request.user)
    #         position = str(Position.objects.get(pk=job.position.id))  # Munkakör megnevezése
    #         position_projects = PositionProject.objects.filter(position=job.position)  # Munkakörhöz tartozó projektek
    #         if not position_projects:
    #             messages.success(request, 'Ehhez a munkakörhöz még nincs rendelve egyetlen projekt sem. '
    #                                       'Jelezd az adminisztrátornak!')
    #             return {'current_year': current_year, 'position': position, 'position_projects': []}
    #         else:
    #             projects = [pp.project for pp in position_projects]
    #             return {'current_year': current_year, 'position': position, 'position_projects': projects}
    #     else:
    #         return {'current_year': current_year, 'position': '--- Válassz munakört! ---', 'position_projects': []}
    # else:
    #     return {'current_year': current_year, 'position': '', 'projects': ''}
