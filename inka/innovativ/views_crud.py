from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from innovativ.form_crud import ProductForm, ProductGroupForm
from innovativ.models import Product, ProductGroup, PriceOffer


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
    return render(request, 'price_offer_update.html', {'price_offer': price_offer})