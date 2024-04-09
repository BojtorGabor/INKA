import csv
import os
from time import sleep

from django.conf import settings
from django.http import JsonResponse

from django.shortcuts import render
from django.contrib import messages

from .forms_projects import CSVFileSelectForm
from .models import Customer


def p_01_1_ugyfel_adat_import(request, project):
    if request.method == 'POST':
        form = CSVFileSelectForm(request.POST, request.FILES)
        if form.is_valid():
            file_name = request.FILES['file'].name
            file_path = os.path.join(settings.BASE_DIR, 'import')
            file_path = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):
                return JsonResponse({'success': False, 'message': 'Az import könytárban nem találtam a kiválasztott fájlt!'})
            else:
                with open(file_path, 'r', encoding='utf-8') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=';')
                    rows = list(csv_reader)
                    total_rows = len(rows)

                    for row_number, row in enumerate(rows, start=1):
                        if len(row) < 6:
                            return JsonResponse({'success': False, 'message': f'Az import fileban ({file_path}) nincs elegendő adat a {row_number}. sorban! A fájlban található összes adat nem került beolvasásra!'})

                        surname, name, email, phone, address, rooftop = row
                        sleep(0.1)
                        # CustomerImport.objects.create(surname=surname, name=name, email=email, phone=phone,
                        #                               address=address, surface=surface)

                        progress = row_number / total_rows * 100
                        print(f'Progress: {progress}')
                        JsonResponse({'success': True, 'progress': progress}, safe=False, status=200)

                return JsonResponse({'success': True, 'message': 'Sikeres importálás.', 'progress': 100})

    else:
        form = CSVFileSelectForm()
    return render(request, 'p_01_1_ugyfel_adat_import_JSON_próba.html', {'project': project, 'form': form})


# def p_01_1_ugyfel_adat_import_items(request, file_path):
#     with open(file_path, 'r', encoding='utf-8') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=';')
#         for row_number, row in enumerate(csv_reader, start=1):
#             if len(row) < 6:
#                 messages.success(request, f'Az import fileban ({file_path}) '
#                                           f'nincs elegendő adat a {row_number}. sorban! '
#                                           f'A fájlban található összes adat nem került beolvasásra!')
#                 return render(request, 'home.html', {})
#         csv_file.seek(0)
#         total_rows = sum(1 for row in csv_reader)
#         csv_file.seek(0)
#
#         for row_number, row in enumerate(csv_reader, start=1):
#             # messages.info(request, f'Adatok importálása... ({row_number}/{total_rows})')
#             surname, name, email, phone, address, surface = row
#             CustomerImport.objects.create(surname= surname, name= name, email= email, phone=phone,
#                                           address=address, surface=surface)
#
#
#         messages.success(request, 'Sikeres importálás.')
#
#     return render(request, 'home.html', {})

def p_02_1_elso_megkereses(request, project):
    cont = '02.1.'
    return render(request, 'project_proba.html', {'project': project})


def p_02_2_adatok_egyeztetese(request, project):
    cont = '02.2.'
    return render(request, 'project_proba.html', {'project': project})


def p_02_3_ugyfel_tipus_meghatarozasa(request, project):
    cont = '02.3.'
    return render(request, 'project_proba.html', {'project': project})


def p_03_1_palyazat_tipusainak_folyamatai(request, project):
    cont = '03.1.'
    return render(request, 'project_proba.html', {'project': project})