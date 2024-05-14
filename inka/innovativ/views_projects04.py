from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction
from django.utils.html import escape

from inka.settings import DEFAULT_FROM_EMAIL
from innovativ.forms_projects import Reason, EmailTemplateForm
from innovativ.models import Task, Project, PriceOffer, PriceOfferItem, EmailTemplate

from inka import settings
import os
import random
import string

from django.core.mail import EmailMessage
from django.template import Template, Context

# @require_http_methods(["GET", "POST"])
def p_04_1_elozetes_arajanlatok(request, task_id):
    task = Task.objects.get(pk=task_id)

    price_offer = PriceOffer.objects.filter(customer=task.customer).order_by('created_at')

    p = Paginator(price_offer, 10)
    page = request.GET.get('page', 1)
    price_offer_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            # Szétválasztjuk az egyedi azonosítót és a művelet nevét
            action_parts = action.split('_')
            action_name = action_parts[0]
            price_offer_id = action_parts[1]

            if action_name == 'makenew':  # Meglévő árajánlatból új előzetes árajánlat készítése
                original_price_offer = PriceOffer.objects.get(pk=price_offer_id)

                # Új pdf fájl létrehozása az eredeti pdf fájlból
                original_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer.id}',
                                                 f'{original_price_offer.file_path}')
                random_filename = generate_random_string() + '.pdf'
                copy_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer.id}', f'{random_filename}')

                # Create a copy of the original PDF
                with open(original_pdf_path, 'rb') as original_pdf:
                    with open(copy_pdf_path, 'wb') as copy_pdf:
                        copy_pdf.write(original_pdf.read())

                # Árajánlat rekord másolatának rögzítése - előzetes árajánlatként
                new_price_offer = PriceOffer.objects.create(type='0:',  # Előzetes árajánlat típus
                                          customer=original_price_offer.customer,
                                          file_path=f'{random_filename}',
                                          currency=original_price_offer.currency,
                                          comment=original_price_offer.comment,
                                          created_user=original_price_offer.created_user)

                # Árajánlat tételek másolatinak rögzítése
                # Az eredeti árajánlat tételei
                original_price_offer_items = PriceOfferItem.objects.filter(price_offer=original_price_offer)
                # Másolat
                copied_records = original_price_offer_items.all()

                # Új rekordok létrehozása a másolat alapján
                with transaction.atomic():  # Biztosítsd az atomi műveletet, hogy az egész tranzakció vagy semmi
                    done = True  # Jelzés, ha nem fut le a tranzakció teljesen
                    for record in copied_records:
                        # Töröld az elsődleges kulcsot, hogy a rekordok újra legyenek generálva
                        record.id = None
                        record.price_offer = new_price_offer
                        try:
                            record.save()
                        except Exception as e:
                            done = False
                if not done:
                    messages.success(request, 'Nem sikerült az új árajánlat tételek létrehozása.')
                    # Az új PriceOffer rekordot is törölni kell ha nem jöttek létre a tételei.
                    delete_price_offer = PriceOffer.objects.get(pk=new_price_offer.id)
                    delete_price_offer.delete()
                else:
                    messages.success(request, f'A {new_price_offer.created_at.date()} - {new_price_offer.id}. '
                                              f'számú új árajánlathoz most még az eredeti pdf fájl tartalma tartozik! '
                                              f'Ne felejtsd el majd aktualizálni a tételek módosítása után!')
            elif action_name == 'update':
                return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
            elif action_name == 'delete':  # Árajánlat törlése
                price_offer = PriceOffer.objects.get(pk=price_offer_id)
                pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer.id}', f'{price_offer.file_path}')
                price_offer.delete()  # Árajánlat rekord és tételeinek törlése
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)  # pdf fájl törlése
                else:
                    messages.success(request, f'{price_offer.file_path} fájl törlés meghiusúlt, '
                                              f'mert nem található az ügyfél könyvtárában!')
            elif action_name == 'send':  # Árajánlat küldése az ügyfélek
                return redirect('p_04_1_elozetes_arajanlat_kuldes', task_id=task.id, price_offer_id=price_offer_id)
            elif action_name == 'accept':  # Elfogadott előzetes lesz az árajánlat
                # Ha van régebbi Elfogadott árajánlat, azt visszaállítani Kiküldöttre
                old_accepted_price_offer = PriceOffer.objects.get(customer=task.customer, type='2:')
                if old_accepted_price_offer:
                    old_accepted_price_offer.type = '1:'
                    old_accepted_price_offer.save()

                    Task.objects.create(type='0:',  # Esemény bejegyzés
                                        type_color='0:',
                                        project=task.project,
                                        customer=task.customer,
                                        comment=f'{task.customer} ügyfél visszavonja a korábban elfogadott - '
                                                f'{old_accepted_price_offer.created_at.date()} - '
                                                f'{old_accepted_price_offer.id}. számú előzetes árajánlat elfogadását.',
                                        created_user=request.user)
                accepted_price_offer = PriceOffer.objects.get(pk=price_offer_id)
                accepted_price_offer.type = '2:'  # Elfogadott előzetes árajánlat lett
                accepted_price_offer.save()

                Task.objects.create(type='0:',  # Esemény bejegyzés
                                    type_color='0:',
                                    project=task.project,
                                    customer=task.customer,
                                    comment=f'{task.customer} ügyfél elfogadta - '
                                            f'{accepted_price_offer.created_at.date()} - '
                                            f'{accepted_price_offer.id}. számú előzetes árajánlatot.',
                                    created_user=request.user)
            elif action_name == 'storno':  # Elfogadott előzetesből Kiküldött előzetes lesz az árajánlat
                accepted_price_offer = PriceOffer.objects.get(pk=price_offer_id)
                accepted_price_offer.type = '1:'  # Kiküldött előzetes árajánlat lett
                accepted_price_offer.save()

                Task.objects.create(type='0:',  # Esemény bejegyzés
                                    type_color='0:',
                                    project=task.project,
                                    customer=task.customer,
                                    comment=f'{task.customer} ügyfél visszavonta - '
                                            f'{accepted_price_offer.created_at.date()} - '
                                            f'{accepted_price_offer.id}. számú előzetes árajánlat elfogadását.',
                                    created_user=request.user)
            elif action_name == 'new':  # Új árajánlat készítése
                # Ha ez az ügyfél első árajánlata, akkor még nincs alkönyvtár a media alatt az ügyfél azonosítójával
                new_directory_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer.id}')
                if not os.path.exists(new_directory_path):
                    # Ha nem létezik, hozzuk létre
                    os.makedirs(new_directory_path)

                # Új üres pdf fájl létrehozása a media/0/EmptyPriceOffer.pdf fájlból
                original_pdf_path = os.path.join(settings.MEDIA_ROOT, '0', 'EmptyPriceOffer.pdf')
                random_filename = generate_random_string() + '.pdf'
                copy_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer.id}', f'{random_filename}')

                # Create a copy of the original PDF
                with open(original_pdf_path, 'rb') as original_pdf:
                    with open(copy_pdf_path, 'wb') as copy_pdf:
                        copy_pdf.write(original_pdf.read())

                # Új árajánlat rekord létrehozása
                new_price_offer = PriceOffer.objects.create(type='0:',  # Előzetes árajánlat típus
                                          customer=task.customer,
                                          file_path=random_filename,
                                          currency='HUF',
                                          comment='',
                                          created_user=request.user)
                messages.success(request, f'A {new_price_offer.created_at.date()} - {new_price_offer.id}. '
                                          f'számú új árajánlathoz most még üres pdf fájl tartozik!'
                                          ' Ne felejtsd el majd aktualizálni a tételek módosítása után!')
                return redirect('price_offer_update', price_offer_id=new_price_offer.id, task_id=task_id)
        return redirect(request.path)  # Frissül az oldal
    return render(request, 'p_04_1_elozetes_arajanlatok.html',
                  {'task': task, 'price_offers': price_offer_page,
                   'page_list': price_offer_page, 'page_range': page_range,})


def p_04_1_elozetes_arajanlat_kuldes(request, task_id, price_offer_id):
    task = Task.objects.get(pk=task_id)
    price_offer = PriceOffer.objects.get(pk=price_offer_id)
    pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer.id}', f'{price_offer.file_path}')

    # a feladathoz tartozó email sablon
    email_template_name = '04.1. Előzetes árajánlat küldése'
    email_template = EmailTemplate.objects.get(title=email_template_name)

    # szerkeszthető szöveg a sblon alapján
    template = Template(email_template.content)

    # az aktuális ügyfélnév helyettesítése a sablon változója alapján
    context = Context({'customer_name': task.customer})
    rendered_content = template.render(context)

    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=email_template)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            updated_content = form.cleaned_data['content']
            to_email = [task.customer.email]

            # Az EmailMessage objektum létrehozása
            email = EmailMessage(
                subject=subject,
                body=updated_content,
                from_email=DEFAULT_FROM_EMAIL,
                to=to_email,
            )
            email.content_subtype = "html"
            # Mellékelt fájl hozzáadása
            email.attach_file(pdf_path)

            # Email elküldése
            sent = email.send()

            if sent:
                messages.success(request, 'E-mail sikeresen elküldve.')

                price_offer.type = '1:'  # Kiküldött előzetes árajánlat lett
                price_offer.save()

                # Az Új feladat jelzőből Folyamatban jelző lesz
                task.type = '3:'
                task.type_color = '3:'
                task.save()

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
                messages.success(request, 'Hiba történt az e-mail küldése közben!')
            return redirect('p_04_1_elozetes_arajanlatok', task_id=task_id)
    else:
        form = EmailTemplateForm(instance=email_template, initial={'content': rendered_content})
    return render(request, 'p_04_1_elozetes_arajanlat_kuldes.html', {'task': task, 'form': form})


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

def generate_random_string(length=20):  # véletlen sztring előállítása a pdf fájlnevekhez
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))