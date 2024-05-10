from django.core.paginator import Paginator
from django.db.models import Sum, F
from django.shortcuts import render, redirect

from innovativ.form_crud import (ProductForm, ProductGroupForm, PriceOfferItemAmountForm, PriceOfferItemPriceForm,
                                 PriceOfferCommentForm)
from innovativ.models import Product, ProductGroup, PriceOffer, PriceOfferItem


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
                PriceOfferItem.objects.create(price_offer=price_offer,)
            elif item_action_name == 'comment':
                return redirect('price_offer_comment', price_offer_id=price_offer_id, task_id=task_id)
            elif item_action_name == 'changemoney':
                pass
            elif item_action_name == 'makepdf':
                pass
            elif item_action_name == 'back':
                return redirect('p_04_1_elozetes_arajanlatok', task_id=task_id)
        return redirect(request.path)  # Frissül az oldal
    return render(request, 'price_offer_update.html',
                  {'price_offer': price_offer, 'price_offer_items': price_offer_item_page,
                   'price_offer_sum_value': price_offer_sum_value['value__sum'],
                   'page_list': price_offer_item_page, 'page_range': page_range,})


def price_offer_item_product(request, price_offer_id, price_offer_item_id, task_id):
    product_group = ProductGroup.objects.all(). order_by('group_name')  # Összes termékcsoport
    price_offer_item = PriceOfferItem.objects.get(pk= price_offer_item_id)  # A módosítandó árajánlat tétel

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
    price_offer_item = PriceOfferItem.objects.get(pk= price_offer_item_id)  # A módosítandó árajánlat tétel

    if request.method == 'POST':
        form = PriceOfferItemAmountForm(request.POST)
        if form.is_valid():
            item_amount = form.cleaned_data['amount']
            price_offer_item.amount = item_amount
            price_offer_item.save()
            return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    else:
        form = PriceOfferItemAmountForm(initial={'amount': price_offer_item.amount})

    return render(request, 'price_offer_item_amount.html',
                  {'price_offer_item': price_offer_item, 'form': form})


def price_offer_item_price(request, price_offer_id, price_offer_item_id, task_id):
    price_offer_item = PriceOfferItem.objects.get(pk= price_offer_item_id)  # A módosítandó árajánlat tétel

    if request.method == 'POST':
        form = PriceOfferItemPriceForm(request.POST)
        if form.is_valid():
            item_price = form.cleaned_data['price']
            price_offer_item.price = item_price
            price_offer_item.save()
            return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    else:
        form = PriceOfferItemPriceForm(initial={'price': price_offer_item.price})

    return render(request, 'price_offer_item_price.html',
                  {'price_offer_item': price_offer_item, 'form': form})


def price_offer_comment(request, price_offer_id, task_id):
    price_offer = PriceOffer.objects.get(pk= price_offer_id)  # A módosítandó árajánlat

    if request.method == 'POST':
        form = PriceOfferCommentForm(request.POST or None, instance=price_offer)
        if form.is_valid():
            form.save()
            return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
    else:
        form = PriceOfferCommentForm(instance=price_offer)

    return render(request, 'price_offer_comment.html',
                  {'price_offer': price_offer, 'form': form})
