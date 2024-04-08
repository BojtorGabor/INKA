import csv
import os
from django.conf import settings

from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone

from .forms_projects import CSVFileSelectForm
from .models import Customer, Task, Project, CustomerHistory


def p_01_1_ugyfel_adat_import(request, project, task_id):  # Új ügyfelek importálása
    task_comment = Task.objects.get(id=task_id)
    if str(task_comment) != 'Állandó feladat: szükség szerint új ügyfelek import fájl bedolgozása.':
        messages.success(request, 'Belső hiba történt, jelezd az adminisztrátornak!')
        messages.success(request, 'Az ügyfél adat import állandó feladat nem található a táblában '
                                  'vagy a szövege megváltozott.')
        return render(request, 'home.html', {})

    if request.method == 'POST':
        form = CSVFileSelectForm(request.POST, request.FILES)  # Import fájl kiválasztása
        if form.is_valid():
            file_name = request.FILES['file'].name
            file_path = os.path.join(settings.BASE_DIR, 'import')
            file_path = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):  # Csak és kizárólag az inka/import/ könyvtárból fogad el import fájlt
                messages.success(request, 'Az import könytárban nem találtam a kiválasztott fájlt!')
            else:
                if p_01_1_ugyfel_adat_import_items(request, file_path, project):  # import fájl feldolgozás
                    return render(request, 'home.html', {})  # sikeres
                else:
                    render(request, 'p_01_1_ugyfel_adat_import.html',
                           {'project': project, 'form': form})  # sikertelen, adatszerkezet hiba?
    else:
        form = CSVFileSelectForm()
    return render(request, 'p_01_1_ugyfel_adat_import.html', {'project': project, 'form': form})


def p_01_1_ugyfel_adat_import_items(request, file_path, project):  # Import fájl ellenőrzés és adatbedolgozás
    with open(file_path, 'r', encoding='utf-8') as csv_file:  # a kiválasztott csv file
        csv_reader = csv.reader(csv_file, delimiter=';')  # pontosvesszővel elválasztva
        for row_number, row in enumerate(csv_reader, start=1):  # jelenleg 6 tételt várok
            if len(row) < 6:
                messages.success(request, f'Az import fájlban ({file_path})'
                                          f' nincs elegendő adat a {row_number}. sorban!')
                messages.success(request, 'FIGYELEM! A fájlban található összes adat nem került beolvasásra!')
                return False
        # csv_file.seek(0)
        # total_rows = sum(1 for row in csv_reader)

        csv_file.seek(0)  # fájl kurzor előre állítása

        next_project = Project.objects.filter(name__startswith='02.1.')  # feladat adás a következő projektnek
        existing_emails = ''  # email ellenőrzéshez, ebben lesz felsorolva ha már volt ilyen email
        new_customer_number = 0
        for row_number, row in enumerate(csv_reader, start=1):  # csv sorokon végigfut
            surname, name, email, phone, address, rooftop = row  # szétbontja a sort
            existing_customer = Customer.objects.filter(email=email)  # email keresés
            if existing_customer.exists():  # már volt ilyen a customer táblában,
                existing_emails = existing_emails + ' -> ' + email  # kigyűjti ezeket az emaileket
            else:  # tényleg új ügyfél
                new_customer_number += 1
                new_customer = Customer.objects.create(surname= surname,
                                                       name= name,
                                                       email= email,
                                                       phone=phone,
                                                       address=address,
                                                       rooftop=rooftop)  # ügyfél felvétele a customer táblába

                CustomerHistory.objects.create(customer=new_customer, history='0.0:')  # Ügyfél történet felvétele

                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer= new_customer,  # ügyfél azonosító
                                    comment=f'Új ügyfelünket: {new_customer} keresd fel adategyeztetés céljából!',
                                    created_user=request.user)
        if existing_emails:  # volt ismétlődő email
            Task.objects.create(type='1:',  # Figyelmeztető bejegyzésés
                                type_color='1:',
                                project=project,
                                comment=f'{file_path}\nfájl importálása során a következő email címek duplikálás miatt '
                                        f'nem kerültek be az ügyfél táblába:\n\n{existing_emails}',
                                created_user=request.user)

            messages.success(request, 'Az importálás csak részben sikeres, voltak duplikált email címek. '
                                      'Ezeket az email címeket megtalálod a Figyelmeztés sorban. ')
        else:
            Task.objects.create(type='4:',  # Sima esemény bejegyzés
                                type_color='4:',
                                project=project,
                                comment=f'{file_path}\n'
                                        f'Össszesen: {new_customer_number} új ügyfél importálása megtörtént.',
                                created_user=request.user,
                                completed_at=timezone.now().isoformat())

            messages.success(request, 'Sikeres importálás.')
    return True


def p_02_1_elso_megkereses(request, project, task_id):
    task = Task.objects.get(pk=task_id)
    return render(request, 'p_02_1_elso_megkereses.html', {'project': project, 'task': task})


def p_02_2_indikativ_arajanlat(request, project, task_id):
    cont = '02.2.'
    return render(request, 'project_proba.html', {'project': project})


def p_02_3_ugyfel_tipus_meghatarozasa(request, project, task_id):
    cont = '02.3.'
    return render(request, 'project_proba.html', {'project': project})


def p_03_1_palyazat_tipusainak_folyamatai(request, project, task_id):
    cont = '03.1.'
    return render(request, 'project_proba.html', {'project': project})