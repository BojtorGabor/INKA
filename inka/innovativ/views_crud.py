from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from innovativ.form_crud import ProductGroupForm
from innovativ.models import ProductGroup


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
                pass

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
    return render(request, 'product_group_update.html', {'form': form})
