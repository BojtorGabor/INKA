import os

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, F
from django.shortcuts import render, redirect

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from num2words import num2words
from django.http import HttpResponse
from io import BytesIO

from inka import settings
from innovativ.form_crud import (ProductForm, ProductGroupForm, PriceOfferItemAmountForm, PriceOfferItemPriceForm,
                                 PriceOfferCommentForm, PriceOfferChangeForm)
from innovativ.models import Product, ProductGroup, PriceOffer, PriceOfferItem, Task, StandardText


def product_crud(request):
    product = Product.objects.select_related('group').order_by('group__group_name', 'name')

    p = Paginator(product, 10)
    page = request.GET.get('page', 1)
    product_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            # Szétválasztjuk az egyedi azonosítót és a művelet nevét
            action_parts = action.split('_')
            action_name = action_parts[0]
            product_id = action_parts[1]

            if action_name == 'new' or action_name == 'update':
                return redirect('product_update', product_id=product_id, action_name=action_name)
            elif action_name == 'delete':
                product = Product.objects.get(id=product_id)
                product.delete()

    return render(request, 'product_crud.html', {'products': product_page,
                                                 'page_list': product_page, 'page_range': page_range, })


def product_update(request, product_id, action_name):
    if action_name == 'update':
        product = Product.objects.get(id=product_id)
    elif action_name == 'new':
        product = ''

    if request.method == 'POST':
        if action_name == 'update':
            form = ProductForm(request.POST or None, instance=product)
        elif action_name == 'new':
            form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_crud')
    else:
        if action_name == 'update':
            form = ProductForm(instance=product)
        elif action_name == 'new':
            form = ProductForm()
    return render(request, 'product_update.html', {'form': form, 'action': action_name})


def product_group_crud(request):
    product_group = ProductGroup.objects.all().order_by('group_name')

    p = Paginator(product_group, 10)
    page = request.GET.get('page', 1)
    product_group_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            # Szétválasztjuk az egyedi azonosítót és a művelet nevét
            action_parts = action.split('_')
            action_name = action_parts[0]
            product_group_id = action_parts[1]

            if action_name == 'new' or action_name == 'update':
                return redirect('product_group_update', product_group_id=product_group_id, action_name=action_name)
            elif action_name == 'delete':
                product_group = ProductGroup.objects.get(id=product_group_id)
                product_group.delete()

    return render(request, 'product_group_crud.html', {'product_groups': product_group_page,
                                                       'page_list': product_group_page, 'page_range': page_range, })


def product_group_update(request, product_group_id, action_name):
    if action_name == 'update':
        product_group = ProductGroup.objects.get(id=product_group_id)
    elif action_name == 'new':
        product_group = ''

    if request.method == 'POST':
        if action_name == 'update':
            form = ProductGroupForm(request.POST or None, instance=product_group)
        elif action_name == 'new':
            form = ProductGroupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('product_group_crud')
    else:
        if action_name == 'update':
            form = ProductGroupForm(instance=product_group)
        elif action_name == 'new':
            form = ProductGroupForm()
    return render(request, 'product_group_update.html', {'form': form, 'action': action_name})


def price_offer_update(request, price_offer_id, task_id):
    price_offer = PriceOffer.objects.get(pk=price_offer_id)
    price_offer_item = (PriceOfferItem.objects.filter(price_offer=price_offer).
                        order_by('product__group__group_name', 'product__name'))
    price_offer_sum_value = PriceOfferItem.objects.filter(price_offer=price_offer).aggregate(value__sum=Sum(
        F('amount') * F('price')))

    total_power = PriceOfferItem.objects.filter(price_offer=price_offer, product__group__group_name='2. Napelem') \
                      .annotate(total_power=F('amount') * F('product__output_power')) \
                      .aggregate(total_power_sum=Sum('total_power'))['total_power_sum'] or 0

    p = Paginator(price_offer_item, 10)
    page = request.GET.get('page', 1)
    price_offer_item_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)

    if request.method == 'POST':
        item_action = request.POST.get('item_action')
        if item_action:
            # Szétválasztjuk az egyedi azonosítót és a művelet nevét
            item_action_parts = item_action.split('_')
            item_action_name = item_action_parts[0]
            price_offer_item_id = item_action_parts[1]

            if item_action_name == 'product':  # Árajánlat tételének Termék kiválasztása
                return redirect('price_offer_item_product', price_offer_id=price_offer_id,
                                price_offer_item_id=price_offer_item_id, task_id=task_id)
            elif item_action_name == 'amount':
                return redirect('price_offer_item_amount', price_offer_id=price_offer_id,
                                price_offer_item_id=price_offer_item_id, task_id=task_id)
            elif item_action_name == 'price':
                return redirect('price_offer_item_price', price_offer_id=price_offer_id,
                                price_offer_item_id=price_offer_item_id, task_id=task_id)
            elif item_action_name == 'delete':
                delete_item = PriceOfferItem.objects.get(pk=price_offer_item_id)
                delete_item.delete()
            elif item_action_name == 'new':  # Új árajánlat tételt vesz fel
                PriceOfferItem.objects.create(price_offer=price_offer, )
                if price_offer.currency != 'HUF':
                    messages.success(request, f'VIGYÁZAT! Az árajánlat {price_offer.currency} pénzegységű, '
                                              f'de az új tétel kiinduló ára még HUF értékben fog megjelenni! '
                                              f'Ne felejtsd el módosítani azt!')
            elif item_action_name == 'comment':
                return redirect('price_offer_comment', price_offer_id=price_offer_id, task_id=task_id)
            elif item_action_name == 'changemoneyHUF-EUR':
                return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
                                change='HUF-EUR')
            elif item_action_name == 'changemoneyHUF-USD':
                return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
                                change='HUF-USD')
            elif item_action_name == 'changemoneyEUR-HUF':
                return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
                                change='EUR-HUF')
            elif item_action_name == 'changemoneyUSD-HUF':
                return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
                                change='USD-HUF')
            elif item_action_name == 'makepdf':
                return redirect('price_offer_makepdf', price_offer_id=price_offer_id, task_id=task_id)
            elif item_action_name == 'back':
                return redirect('p_04_1_elozetes_arajanlatok', task_id=task_id)
        return redirect(request.path)  # Frissül az oldal
    return render(request, 'price_offer_update.html',
                  {'price_offer': price_offer, 'price_offer_items': price_offer_item_page,
                   'price_offer_sum_value': price_offer_sum_value['value__sum'],
                   'total_power': total_power,
                   'page_list': price_offer_item_page, 'page_range': page_range, })


def price_offer_item_product(request, price_offer_id, price_offer_item_id, task_id):
    product_group = ProductGroup.objects.all().order_by('group_name')  # Összes termékcsoport
    price_offer_item = PriceOfferItem.objects.get(pk=price_offer_item_id)  # A módosítandó árajánlat tétel

    if request.method == 'POST':
        product_action = request.POST.get('product_action')  # Product.id-vel jön vissza
        product = Product.objects.get(pk=product_action)  # A kiválasztott termék
        price_offer_item.product = product  # Árajánlat tételének termék beállítása
        price_offer_item.price = product.price  # A termék alapértelmezett árának beállítása
        price_offer_item.save()
        return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    return render(request, 'price_offer_item_product.html',
                  {'product_groups': product_group, 'price_offer_item': price_offer_item})


def price_offer_item_amount(request, price_offer_id, price_offer_item_id, task_id):
    price_offer_item = PriceOfferItem.objects.get(pk=price_offer_item_id)  # A módosítandó árajánlat tétel
    product = price_offer_item.product
    unit_choice = product.get_unit_display()

    if request.method == 'POST':
        form = PriceOfferItemAmountForm(request.POST or None, instance=price_offer_item)
        if form.is_valid():
            form.save()
            return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    else:
        form = PriceOfferItemAmountForm(instance=price_offer_item)

    return render(request, 'price_offer_item_amount.html',
                  {'price_offer_item': price_offer_item, 'form': form, 'unit_choice': unit_choice})


def price_offer_item_price(request, price_offer_id, price_offer_item_id, task_id):
    price_offer_item = PriceOfferItem.objects.get(pk=price_offer_item_id)  # A módosítandó árajánlat tétel
    price_offer = PriceOffer.objects.get(pk=price_offer_id)
    currency = price_offer.currency

    if request.method == 'POST':
        form = PriceOfferItemPriceForm(request.POST or None, instance=price_offer_item)
        if form.is_valid():
            form.save()
            return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    else:
        form = PriceOfferItemPriceForm(instance=price_offer_item)

    return render(request, 'price_offer_item_price.html',
                  {'price_offer_item': price_offer_item, 'form': form, 'currency': currency})


def price_offer_comment(request, price_offer_id, task_id):
    price_offer = PriceOffer.objects.get(pk=price_offer_id)  # A módosítandó árajánlat

    if request.method == 'POST':
        form = PriceOfferCommentForm(request.POST or None, instance=price_offer)
        if form.is_valid():
            form.save()
            return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    else:
        form = PriceOfferCommentForm(instance=price_offer)

    return render(request, 'price_offer_comment.html',
                  {'price_offer': price_offer, 'form': form})


def price_offer_change_money(request, price_offer_id, task_id, change):
    price_offer = PriceOffer.objects.get(pk=price_offer_id)  # A módosítandó árajánlat

    if change == 'HUF-EUR':
        new_currency = 'EUR'
        foreign_currency = 'EUR'
    elif change == 'HUF-USD':
        new_currency = 'USD'
        foreign_currency = 'USD'
    elif change == 'EUR-HUF':
        new_currency = 'HUF'
        foreign_currency = 'EUR'
    elif change == 'USD-HUF':
        new_currency = 'HUF'
        foreign_currency = 'USD'

    if request.method == 'POST':
        form = PriceOfferChangeForm(request.POST or None, instance=price_offer)
        if form.is_valid():
            if change == 'HUF-EUR' or change == 'HUF-USD':
                num_updated = (PriceOfferItem.objects.filter(price_offer=price_offer)
                               .update(price=F('price') / price_offer.change_rating))
            else:
                num_updated = (PriceOfferItem.objects.filter(price_offer=price_offer)
                               .update(price=F('price') * price_offer.change_rating))
            if num_updated != 0:
                price_offer.currency = new_currency
                form.save()
                messages.success(request, f'Átváltottad az árajánlatot ({change})')
            else:
                messages.success(request, f'Nem sikerült az tételek átváltása ({change})')
            return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    else:
        form = PriceOfferChangeForm(instance=price_offer)

    return render(request, 'price_offer_change.html',
                  {'price_offer': price_offer, 'form': form, 'change': change, 'foreign_currency': foreign_currency})


def price_offer_makepdf(request, price_offer_id, task_id):
    task = Task.objects.get(pk=task_id)
    price_offer = PriceOffer.objects.get(pk=price_offer_id)
    price_offer_items = (PriceOfferItem.objects.filter(price_offer=price_offer).
                        order_by('product__group__group_name', 'product__name'))
    currency = price_offer.currency
    if currency == 'HUF':
        tizedes = 0
    else:
        tizedes = 2
    standard_text = StandardText.objects.get(title='Árajánlat alján szöveg')
    output_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer_project.customer.id}',
                                   f'{price_offer.file_path}')

    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'  # A PDF-et letölthető fájlként nyitja meg
    # response['Content-Disposition'] = 'inline; filename="generated_pdf.pdf"'  # Ez a beállítás megnyitja a PDF-et az aktuális fülön

    buffer = BytesIO()
    pdf = canvas.Canvas(output_pdf_path, pagesize=A4, bottomup=0)
    width, height = A4

    # Betűtípus regisztrálása
    pdfmetrics.registerFont(TTFont('OpenSans-Regular', 'static/fonts/OpenSans-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSans-Bold', 'static/fonts/OpenSans-Bold.ttf'))

    # Fejléc hozzáadása minden oldalra
    def add_header_footer(can, page_numb):  # Fejléc generálás
        can.saveState()
        can.setFont("OpenSans-Bold", 30)
        can.drawString(230, 90, 'Árajánlat')

        can.rect(30, 30, 535, 780)  # külső keret

        can.rect(30, 120, 535, 60)

        can.setFont("OpenSans-Regular", 10)
        can.drawString(40, 135, 'Kibocsátó:')
        can.drawString(310, 135, 'Vevő:')

        can.setFont("OpenSans-Bold", 10)
        can.drawString(60, 146, 'Innovatív Napelem Kft.')
        can.drawString(60, 158, '2400 Dunaújváros, Barátság út 5. fszt. 1.')
        can.drawString(60, 170, 'Adószám: 26350350-2-07')
        can.drawString(330, 150, f'{price_offer.customer_project.customer}')
        can.drawString(330, 165, f'{price_offer.customer_project.customer.address}')

        can.setFillColorRGB(0.8, 0.8, 0.8)
        can.rect(30, 180, 535, 30, fill=1)  # 2. sor színezve
        can.setFillColorRGB(0, 0, 0)

        can.line(165, 180, 165, 210)  # 1. függőleges vonal
        can.line(300, 120, 300, 210)  # 2. függőleges vonal
        can.line(490, 180, 490, 210)  # 3. függőleges vonal

        can.setFont("OpenSans-Regular", 10)
        can.drawString(50, 200, f'Kiállítás: {price_offer.created_at.strftime("%Y-%m-%d")}')  # kiállítás dátume
        can.drawString(190, 200, 'Érvényes 30 napig')  # érvényes
        can.drawString(350, 200, f'Árajánlat száma: {price_offer.id}')  # árajánlat száma
        can.drawString(510, 200, f'{page_numb}. oldal')  # oldalszámozás

        can.setFont("OpenSans-Bold", 10)
        can.drawString(40, 230, 'Megnevezés')
        can.drawString(140, 230, 'Áfa')
        can.drawRightString(230, 230, 'Nettó ár')
        can.drawRightString(230, 245, '(' + f'{currency}' + ')')
        can.drawRightString(290, 230, 'Menny.')
        can.drawRightString(380, 230, 'Nettó érték')
        can.drawRightString(380, 245, '(' + f'{currency}' + ')')
        can.drawRightString(460, 230, 'Áfa tartalom')
        can.drawRightString(460, 245, '(' + f'{currency}' + ')')
        can.drawRightString(550, 230, 'Bruttó érték')
        can.drawRightString(550, 245, '(' + f'{currency}' + ')')

        can.line(30, 250, 565, 250)  # 1. vízszintes vonal
        can.restoreState()
        can.setFont("OpenSans-Regular", 10)

    y_position = 265  # Kezdeti pozíció a fejléc alatt
    page_numb = 1
    item_number = 1
    sum_netto_ertek = 0
    sum_afa_ertek = 0
    sum_brutto_ertek = 0
    pdf.setFont("OpenSans-Regular", 10)
    add_header_footer(pdf, page_numb)  # Fejléc az első oldalra
    for price_offer_item in price_offer_items:
        if y_position > height-70:  # Ellenőrizzük, hogy van-e hely az aktuális oldalon
            # pdf.drawString(40, y_position, 'Folytatás a következő oldalon...')
            pdf.showPage()
            page_numb += 1
            add_header_footer(pdf, page_numb)
            y_position = 265  # Új oldal kezdeti pozíciója

        starting_y_position = y_position - 11
        y_height = 30
        if not price_offer_item.product == None:  # Ha nem N/A még a tétel
            if price_offer_item.product.comment:
                y_height += 15
            if item_number % 2 == 0:  # páros sor
                pdf.setFillColorRGB(0.9, 0.9, 0.9)
            else:
                pdf.setFillColorRGB(0.8, 0.8, 0.8)
            pdf.rect(31, starting_y_position, 533, y_height, fill=1, stroke=0)  #
            pdf.setFillColorRGB(0, 0, 0)

            pdf.drawString(40, y_position, str(price_offer_item))
            y_position += 15  # Következő sor pozíciója
            if price_offer_item.product.comment:
                pdf.drawString(60, y_position, str(price_offer_item.product.comment))  # Termék megjegyzés
                y_position += 15  # Következő sor pozíciója

            pdf.drawString(140, y_position, '27%')  # Áfa

            formatted_number = f'{price_offer_item.price:,.{tizedes}f}'.replace(",", " ")
            pdf.drawRightString(230, y_position, formatted_number)  # Nettó ár

            unit_display = price_offer_item.product.get_unit_display()  # Mértékegység
            formatted_number = f'{price_offer_item.amount:,.0f}'.replace(",", " ") + ' ' + unit_display
            pdf.drawRightString(290, y_position, formatted_number)  # Mennyiség

            netto_ertek = price_offer_item.price * price_offer_item.amount
            sum_netto_ertek += netto_ertek
            formatted_number = f'{netto_ertek:,.{tizedes}f}'.replace(",", " ")
            pdf.drawRightString(380, y_position, formatted_number)  # Nettó érték

            afa_ertek = round(int(netto_ertek) * 0.27)
            sum_afa_ertek += afa_ertek
            formatted_number = f'{afa_ertek:,.{tizedes}f}'.replace(",", " ")
            pdf.drawRightString(460, y_position, formatted_number)  # Áfa érték

            brutto_ertek = netto_ertek + afa_ertek
            sum_brutto_ertek += brutto_ertek
            formatted_number = f'{brutto_ertek:,.{tizedes}f}'.replace(",", " ")
            pdf.drawRightString(550, y_position, formatted_number)  # Bruttó érték

            y_position += 15  # Következő sor pozíciója
            item_number += 1

    if y_position > height-105:  # Ellenőrizzük, hogy van-e hely az aktuális oldalon
        # pdf.drawString(40, y_position, 'Folytatás a következő oldalon...')
        pdf.showPage()
        page_numb += 1
        add_header_footer(pdf, page_numb)
        y_position = 265  # Új oldal kezdeti pozíciója

    pdf.setFont("OpenSans-Bold", 10)

    y_position += 15  # Következő sor pozíciója
    pdf.drawRightString(450, y_position, 'Nettó összesen:')
    formatted_number = f'{sum_netto_ertek:,.{tizedes}f}'.replace(",", " ") + ' ' + f'{currency}'
    pdf.drawRightString(550, y_position, formatted_number)  # Nettó összérték

    y_position += 15  # Következő sor pozíciója
    pdf.drawRightString(450, y_position, 'Áfa tartalom összesen:')
    formatted_number = f'{sum_afa_ertek:,.{tizedes}f}'.replace(",", " ") + ' ' + f'{currency}'
    pdf.drawRightString(550, y_position, formatted_number)  # Áfa összérték

    y_position += 15  # Következő sor pozíciója
    pdf.drawRightString(450, y_position, 'Bruttó összesen:')
    formatted_number = f'{sum_brutto_ertek:,.{tizedes}f}'.replace(",", " ") + ' ' + f'{currency}'
    pdf.drawRightString(550, y_position, formatted_number)  # Bruttó összérték

    pdf.setFont("OpenSans-Regular", 8)
    y_position += 15  # Következő sor pozíciója
    text_brutto_ertek = 'azaz ' + num2words(round(sum_brutto_ertek, tizedes), lang='hu') + ' ' + currency
    pdf.drawRightString(550, y_position, text_brutto_ertek)  # Bruttó összérték szöveggel

    if y_position > height - 75:  # Ellenőrizzük, hogy van-e hely az aktuális oldalon
        # pdf.drawString(40, y_position, 'Folytatás a következő oldalon...')
        pdf.showPage()
        page_numb += 1
        add_header_footer(pdf, page_numb)
        y_position = 265  # Új oldal kezdeti pozíciója

    pdf.setFont("OpenSans-Regular", 10)
    y_position += 60  # Következő sor pozíciója
    pdf.line(40, y_position, 240, y_position)
    pdf.line(350, y_position, 550, y_position)

    y_position += 15  # Következő sor pozíciója
    pdf.drawString(120, y_position, 'Kibocsátó')
    pdf.drawString(440, y_position, 'Vevő')
    y_position += 15  # Következő sor pozíciója


    if y_position > height - 220:  # Ellenőrizzük, hogy van-e hely az aktuális oldalon
        # pdf.drawString(40, y_position, 'Folytatás a következő oldalon...')
        pdf.showPage()
        page_numb += 1
        add_header_footer(pdf, page_numb)
        y_position = 265  # Új oldal kezdeti pozíciója

    y_position += 15  # Következő sor pozíciója
    text = pdf.beginText(40, y_position)
    for line in standard_text.content.splitlines():
        text.textLine(line)
        y_position += 10  # Sorok közötti távolság
    pdf.drawText(text)

    pdf.showPage()
    pdf.save()

    # Olvasd be a mentett PDF-et, hogy response-t küldhess
    # with open(output_pdf_path, 'rb') as f:
    #     pdf_content = f.read()
    #
    # response.write(pdf_content)
    # return response

    messages.success(request, f'Sikeres PDF aktualizálás.')

    return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)


# def price_offer_makepdf(request, price_offer_id, task_id):  # PDF sablonba beírás próba
#     task = Task.objects.get(pk=task_id)
#     price_offer = PriceOffer.objects.get(pk=price_offer_id)
#
#     # Olvasd be a meglévő PDF fájlt
#     template_pdf_path = os.path.join(settings.MEDIA_ROOT, '0', 'EmptyPriceOffer.pdf')
#     template_pdf = PdfReader(template_pdf_path)
#
#     # Regisztráld a betűtípust
#     pdfmetrics.registerFont(TTFont('DejaVu', os.path.join(settings.MEDIA_ROOT, '0', 'dejavu-sans.book.ttf')))
#
#     # Készíts egy új PDF fájlt a Reportlab segítségével, és adj hozzá adatokat
#     packet = BytesIO()
#     can = canvas.Canvas(packet, pagesize=A4, bottomup=0)
#
#     # Beállítjuk a betűtípust, amely támogatja a magyar ékezetes karaktereket
#     can.setFont("DejaVu", 12)
#     # can.drawString(100, 100, "aAáÁeEéÉiIíÍoOóÓöÖőŐuUúÚüÜűŰ.")
#     can.save()
#
#     # Állítsd a buffer-t a kezdő pozícióra
#     packet.seek(0)
#     new_pdf = PdfReader(packet)
#
#     # Az első oldal hozzáadása a meglévő PDF-hez
#     output = PdfWriter()
#     for page_num in range(len(template_pdf.pages)):
#         page = template_pdf.pages[page_num]
#         # Új oldal hozzáadása az eredeti oldalakhoz
#         if page_num == 0:
#             page.merge_page(new_pdf.pages[0])
#         output.add_page(page)
#
#     # Mentsd el az új PDF fájlt más néven
#     output_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer_project.customer.id}', f'{price_offer.file_path}')
#
#     with open(output_pdf_path, "wb") as output_pdf:
#         output.write(output_pdf)
#
#     return render(request, 'home.html', {})
