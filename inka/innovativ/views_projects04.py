from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_http_methods
from innovativ.forms_projects import Reason
from innovativ.models import Task, Project, PriceOffer, PriceOfferItem

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

            print('Árajánlat akció', action_name)
            print('Árajánlat', price_offer_id)

            if action_name == 'makenew':  # Meglévő árajánlatból új előzetes árajánlat készítése
                original_price_offer = PriceOffer.objects.get(pk=price_offer_id)
                # Árajánlat rekord másolatának rögzítése - előzetes árajánlatként
                new_price_offer = PriceOffer.objects.create(type='0:',  # Előzetes árajánlat típus
                                          customer=original_price_offer.customer,
                                          file_path=original_price_offer.file_path,  # Ez eredeti pdf-et hozza be ide
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
                    messages.success(request, 'Az új árajánlathoz most még az eredeti pdf fájl tartozik! '
                                              'Ne felejtsd el majd azt újra elkészíteni a tételek módosítása után!')
            elif action_name == 'update':
                return redirect('price_offer_update', price_offer_id=price_offer_id)
            elif action_name == 'delete':
                pass
            elif action_name == 'send':
                pass
            elif action_name == 'accept':
                pass
            elif action_name == 'new':
                pass
            elif action_name == 'comment':
                pass
        return redirect(request.path)
    return render(request, 'p_04_1_elozetes_arajanlatok.html',
                  {'task': task, 'price_offers': price_offer_page,
                   'page_list': price_offer_page, 'page_range': page_range,})

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
