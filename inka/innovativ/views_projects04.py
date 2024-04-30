from django.contrib import messages
from django.shortcuts import render
from django.utils import timezone

from innovativ.forms_projects import Reason
from innovativ.models import Task, Project


def p_04_1_elozetes_arajanlatok(request, task_id):
    task = Task.objects.get(pk=task_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            # Szétválasztjuk az egyedi azonosítót és a művelet nevét
            action_parts = action.split('_')
            action_name = action_parts[0]
            price_offer_id = action_parts[1]

            if action_name == 'new':
                pass
            elif action_name == 'update':
                pass
            elif action_name == 'send':
                pass
            elif action_name == 'accept':
                pass
    return render(request, 'p_04_1_elozetes_arajanlatok.html', {'task': task})

def p_04_1_ugyfel_visszaadasa_02_nek(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = Reason(request.POST)
            if form.is_valid():
                task.type = '4:'
                task.type_color = '4:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # feladat visszaadása 02. Ügyfél adatainak felelőséhez
                next_project = Project.objects.filter(name__startswith='02.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer=task.customer,  # ügyfél azonosító
                                    comment=f'{ task.customer } - Az előzetes árajánlat nem készíthető el.\n'
                                            f'{form["reason"].value()}',
                                    created_user=request.user)
                return render(request, 'home.html', {})
        else:
            form = Reason()

        return render(request, 'p_04_1_ugyfel_visszaadása_02_nek.html', {'task': task, 'form': form})
