from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template import Template, Context
from django.utils import timezone

from .forms_projects import EmailTemplateForm, CustomerForm, Reason
from .models import Task, EmailTemplate, Customer, Project
from django.core.mail import send_mail

from inka.settings import DEFAULT_FROM_EMAIL


def p_02_1_telefonos_megkereses(request, task_id):
    # az aktuális ügyfél
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        customer = task.customer
        old_email = customer.email
        ok = False

        if request.method == 'POST':
            form = CustomerForm(request.POST, instance=customer)
            email = request.POST.get('email')
            if old_email != email:  # ha változott az email cím
                try:
                    Customer.objects.get(email=email)  # az új email már létezik a rendszerben
                    messages.success(request, f'A(z) {email} email cím már szerepel a rendszerben.')
                except ObjectDoesNotExist:  # az új email még nincs a rendszerben
                    ok = True
            else:
                ok = True

            if ok and form.is_valid():
                if form.has_changed():
                    form.save()
                    messages.success(request, 'Ügyfél adatai aktualizálva.')
                    # Feladat átállítva Folyamatban értékre
                    task.type = '3:'
                    task.type_color = '3:'
                    task.save()

                    Task.objects.create(type='0:',  # Esemény bejegyzésés
                                        type_color='0:',
                                        project=task.project,
                                        customer=task.customer,
                                        comment=f'{task.customer} ügyfél adatainak aktualizálása történt.',
                                        created_user=request.user)
                else:
                    messages.success(request, 'Ügyfél adatai nem változtak.')
            return render(request, 'home.html', {})
        else:
            form = CustomerForm(instance=customer)

        return render(request, 'p_02_1_telefonos_megkereses.html', {'task': task, 'form': form})


def p_02_1_telefonszam_keres(request, task_id):
    # az aktuális ügyfél
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        # a feladathoz tartozó email sablon
        email_template_name = '02.1. Email kérés elérhető telefonszámért'
        email_template = EmailTemplate.objects.get(title=email_template_name)

        # szerkeszthető szöveg a sblon alapján
        template = Template(email_template.content)

        # az aktuális ügyfélnév helyettesítése a sablon változója alapján
        context = Context({'customer_name': task.customer})
        rendered_content = template.render(context)

        if request.method == 'POST':
            form = EmailTemplateForm(request.POST, instance=email_template)
            if form.is_valid():
                subject = form['subject'].value()
                message = form['content'].value()
                to_email = [task.customer.email]
                sent = send_mail(subject, message, DEFAULT_FROM_EMAIL, to_email, html_message=message)
                # Az Új feladat jelzőből Folyamatban jelző lesz
                task.type = '3:'
                task.type_color = '3:'
                task.save()
                if sent:
                    messages.success(request, 'E-mail sikeresen elküldve.')
                    Task.objects.create(type='0:',  # Esemény bejegyzés
                                        type_color='0:',
                                        project=task.project,
                                        customer=task.customer,
                                        comment=f'{task.customer} ügyfélnek - {email_template_name} - '
                                                f'nevű sablon email sikeresen kiküldve.',
                                        created_user=request.user)
                else:
                    Task.objects.create(type='1:',  # Figyelmeztető bejegyzés
                                        type_color='1:',
                                        project=task.project,
                                        customer=task.customer,
                                        comment=f'{task.customer} ügyfélnek - {email_template_name} - '
                                            f'nevű sablon küldése nem sikerült.',
                                        created_user=request.user)
                    messages.success(request,'Hiba történt az e-mail küldése közben!')
                return render(request, 'home.html', {})
        else:
            form = EmailTemplateForm(instance=email_template, initial={'content': rendered_content})
        return render(request, 'p_02_1_telefonszam_keres.html', {'task': task, 'form': form})


def p_02_1_ugyfelnek_elozetes_arajanlat(request, task_id):
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

                # feladat adás az Előzetes árajánlat adás projektnek
                next_project = Project.objects.filter(name__startswith='04.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer=task.customer,  # ügyfél azonosító
                                    comment=f'{ task.customer } - ügyfelünknek adj előzetes árajánlatot.\n{form["reason"].value()}',
                                    created_user=request.user)
                return render(request, 'home.html', {})
        else:
            form = Reason()

        return render(request, 'p_02_1_ugyfelnek_elozetes_arajanlat.html',
                      {'task': task, 'form': form})


def p_02_1_ugyfelnek_felmeres(request, task_id):
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

                # feladat adás az Felmérő kiválasztása projektnek
                next_project = Project.objects.filter(name__startswith='05.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer=task.customer,  # ügyfél azonosító
                                    comment=f'{ task.customer } - ügyfelünknek szervezz felmérést.\n{form["reason"].value()}',
                                    created_user=request.user)
                return render(request, 'home.html', {})
        else:
            form = Reason()

        return render(request, 'p_02_1_ugyfelnek_felmeres.html',
                      {'task': task, 'form': form})


def p_02_1_ugyfel_elerhetetlen(request, task_id):
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

                # feladat adás az Ügyfél adatlap megszüntetése projektnek
                next_project = Project.objects.filter(name__startswith='20.1.')
                Task.objects.create(type='2:',  # Feladat típus
                                    type_color='2:',
                                    project=next_project[0],  # következő projekt
                                    customer=task.customer,  # ügyfél azonosító
                                    comment=f'{ task.customer } - Az ügyfél elérhetetlen, kérem az adatlap törlését.\n'
                                            f'{form["reason"].value()}',
                                    created_user=request.user)
                return render(request, 'home.html', {})
        else:
            form = Reason()

        return render(request, 'p_02_1_ugyfel_elerhetetlen.html', {'task': task, 'form': form})


def p_02_2_uj_feladat(request):
    if request.user.is_authenticated:
        customer_set = ''
        if request.method == 'POST':
            action = request.POST.get('action')
            if action:
                # Szétválasztjuk az egyedi azonosítót és a művelet nevét
                action_parts = action.split('_')
                action_name = action_parts[0]
                customer_id = action_parts[1]

                if action_name == 'search':
                    searched = request.POST['searched']
                    customer_set = (Customer.objects.filter(
                        Q(surname__icontains=searched) |
                        Q(name__icontains=searched) |
                        Q(email__icontains=searched) |
                        Q(phone__icontains=searched) |
                        Q(address__icontains=searched) |
                        Q(installation_address__icontains=searched))
                                    .order_by('surname', 'name'))
                elif action_name == 'new':
                    project = Project.objects.get(name='02.2. Újabb megkeresés')
                    customer = Customer.objects.get(pk=customer_id)
                    reason = request.POST['reason']
                    Task.objects.create(type='2:',  # Feladat típus
                                        type_color='2:',
                                        project=project,  # következő projekt
                                        customer=customer,  # ügyfél azonosító
                                        comment=f'{customer} - ügyfelünk új feladatot kezdeményezett.\n{reason}',
                                        created_user=request.user)
                    messages.success(request, f'{customer} ügyfél részére új feladatot indítottál el.')
                    return render(request, 'home.html', {})
                else:
                    customer_set = ''

        p = Paginator(customer_set, 10)
        page = request.GET.get('page', 1)
        customer_page = p.get_page(page)
        page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

        return render(request, 'p_02_2_uj_feladat.html', {'customers': customer_page,
                                              'page_list': customer_page, 'page_range': page_range})
    else:
        messages.success(request, 'Nincs jogosultságod.')
        return redirect('login')


def p_02_2_uj_megkereses_igenye(request, task_id):
    task = Task.objects.get(pk=task_id)
    customer = Customer.objects.get(pk=task.customer.id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = Reason(request.POST)
            if form.is_valid():
                customer.request = form['reason'].value()
                customer.save()
                # bejegyzés a törlésről
                project = task.project
                # Task.objects.create(type='0:',  # Feladat típus
                #                     type_color='0:',
                #                     project=project,  # projekt
                #                     customer=task.customer,  # ügyfél azonosító
                #                     comment=f'{ task.customer } - ügyfelünk új feladat kérése törölve.'
                #                             f'\n{form["reason"].value()}',
                #                     created_user=request.user)
                return render(request, 'home.html', {})
        else:
            form = Reason(initial={'reason': customer.request})

        return render(request, 'p_02_2_uj_megkereses_igenye.html',
                      {'task': task, 'form': form})


def p_02_2_uj_megkereses_torlese(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task.completed_at:
        messages.success(request, f'Ez a projekt már elkészült '
                                  f'{task.completed_at.strftime("%Y.%m.%d. %H:%M")}-kor.')
        return render(request, 'home.html', {})
    else:
        if request.method == 'POST':
            form = Reason(request.POST)
            if form.is_valid():
                task.type = '5:'
                task.type_color = '5:'
                task.completed_at = timezone.now().isoformat()
                task.save()

                # bejegyzés a törlésről
                project = task.project
                Task.objects.create(type='0:',  # Feladat típus
                                    type_color='0:',
                                    project=project,  # projekt
                                    customer=task.customer,  # ügyfél azonosító
                                    comment=f'{ task.customer } - ügyfelünk új feladat kérése törölve.'
                                            f'\n{form["reason"].value()}',
                                    created_user=request.user)
                return render(request, 'home.html', {})
        else:
            form = Reason()

        return render(request, 'p_02_2_uj_megkereses_torlese.html',
                      {'task': task, 'form': form})
