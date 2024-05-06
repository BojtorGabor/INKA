from django.core.paginator import Paginator
from django.db.models import Sum, F
from django.shortcuts import render, redirect

from innovativ.form_crud import ProductForm, ProductGroupForm
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


def price_offer_update(request, price_offer_id):
    price_offer = PriceOffer.objects.get(pk=price_offer_id)
    price_offer_item = PriceOfferItem.objects.filter(price_offer=price_offer).order_by('product__name')
    price_offer_sum_value = PriceOfferItem.objects.filter(price_offer=price_offer).aggregate(value__sum=Sum(
        F('amount') * F('price')))

    p = Paginator(price_offer_item, 10)
    page = request.GET.get('page', 1)
    price_offer_item_page = p.get_page(page)
    page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)


    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            # Szétválasztjuk az egyedi azonosítót és a művelet nevét
            action_parts = action.split('_')
            action_name = action_parts[0]
            price_offer_item_id = action_parts[1]

            print('árajánlat tétel akció', action_name)
            print('Árajánlat tétel', price_offer_item_id)

            if action_name == 'new' or action_name == 'update':
                # return redirect('product_update', product_id=product_id, action_name=action_name)
                pass
            elif action_name == 'delete':
                pass
            elif action_name == 'comment':
                pass
            elif action_name == 'makepdf':
                pass

    return render(request, 'price_offer_update.html',
                  {'price_offer': price_offer, 'price_offer_items': price_offer_item_page,
                   'price_offer_sum_value': price_offer_sum_value['value__sum'],
                   'page_list': price_offer_item_page, 'page_range': page_range,})
