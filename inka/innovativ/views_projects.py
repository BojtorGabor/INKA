import csv
import os
from django.conf import settings

from django.shortcuts import render
from django.contrib import messages

from .forms_projects import CSVFileSelectForm
from .models import Customer, Task, Project


def p_01_1_ugyfel_adat_import(request, project):
    if request.method == 'POST':
        form = CSVFileSelectForm(request.POST, request.FILES)
        if form.is_valid():
            file_name = request.FILES['file'].name
            file_path = os.path.join(settings.BASE_DIR, 'import')
            file_path = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):
                messages.success(request, 'Az import könytárban nem találtam a kiválasztott fájlt!')
            else:
                # Itt továbbíthatod a fájlnévet a feldolgozó nézetnek
                # messages.success(request, 'Importálás...')
                if p_01_1_ugyfel_adat_import_items(request, file_path, project):
                    return render(request, 'home.html', {})
                else:
                    render(request, 'p_01_1_ugyfel_adat_import.html',
                           {'project': project, 'form': form})
    else:
        form = CSVFileSelectForm()
    return render(request, 'p_01_1_ugyfel_adat_import.html', {'project': project, 'form': form})


def p_01_1_ugyfel_adat_import_items(request, file_path, project):
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row_number, row in enumerate(csv_reader, start=1):
            if len(row) < 6:
                messages.success(request, f'Az import fájlban ({file_path}) nincs elegendő adat a {row_number}. sorban!')
                messages.success(request, 'FIGYELEM! A fájlban található összes adat nem került beolvasásra!')
                return False
        csv_file.seek(0)
        total_rows = sum(1 for row in csv_reader)
        csv_file.seek(0)

        Task.objects.create(type='1:', project= project, comment=f'{file_path} fájl importálása megtörtént.',
                            created_user= request.user)

        for row_number, row in enumerate(csv_reader, start=1):
            # messages.info(request, f'Adatok importálása... ({row_number}/{total_rows})')
            surname, name, email, phone, address, rooftop = row
            # CustomerImport.objects.create(surname= surname, name= name, email= email, phone=phone,
            #                               address=address, rooftop=rooftop)
        messages.success(request, 'Sikeres importálás.')

    return True


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