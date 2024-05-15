# import os
#
# from django.contrib import messages
# from django.core.paginator import Paginator
# from django.db.models import Sum, F
# from django.shortcuts import render, redirect
#
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate
#
# from inka import settings
# from innovativ.form_crud import (ProductForm, ProductGroupForm, PriceOfferItemAmountForm, PriceOfferItemPriceForm,
#                                  PriceOfferCommentForm, PriceOfferChangeForm)
# from innovativ.models import Product, ProductGroup, PriceOffer, PriceOfferItem, Task
#
#
# def product_crud(request):
#     product = Product.objects.select_related('group').order_by('group__group_name', 'name')
#
#     p = Paginator(product, 10)
#     page = request.GET.get('page', 1)
#     product_page = p.get_page(page)
#     page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)
#
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         if action:
#             # Szétválasztjuk az egyedi azonosítót és a művelet nevét
#             action_parts = action.split('_')
#             action_name = action_parts[0]
#             product_id = action_parts[1]
#
#             if action_name == 'new' or action_name == 'update':
#                 return redirect('product_update', product_id=product_id, action_name=action_name)
#             elif action_name == 'delete':
#                 product = Product.objects.get(id=product_id)
#                 product.delete()
#
#     return render(request, 'product_crud.html', {'products': product_page,
#                                                  'page_list': product_page, 'page_range': page_range, })
#
#
# def product_update(request, product_id, action_name):
#     if action_name == 'update':
#         product = Product.objects.get(id=product_id)
#     elif action_name == 'new':
#         product = ''
#
#     if request.method == 'POST':
#         if action_name == 'update':
#             form = ProductForm(request.POST or None, instance=product)
#         elif action_name == 'new':
#             form = ProductForm(request.POST)
#
#         if form.is_valid():
#             form.save()
#             return redirect('product_crud')
#     else:
#         if action_name == 'update':
#             form = ProductForm(instance=product)
#         elif action_name == 'new':
#             form = ProductForm()
#     return render(request, 'product_update.html', {'form': form, 'action': action_name})
#
#
# def product_group_crud(request):
#     product_group = ProductGroup.objects.all().order_by('group_name')
#
#     p = Paginator(product_group, 10)
#     page = request.GET.get('page', 1)
#     product_group_page = p.get_page(page)
#     page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)
#
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         if action:
#             # Szétválasztjuk az egyedi azonosítót és a művelet nevét
#             action_parts = action.split('_')
#             action_name = action_parts[0]
#             product_group_id = action_parts[1]
#
#             if action_name == 'new' or action_name == 'update':
#                 return redirect('product_group_update', product_group_id=product_group_id, action_name=action_name)
#             elif action_name == 'delete':
#                 product_group = ProductGroup.objects.get(id=product_group_id)
#                 product_group.delete()
#
#     return render(request, 'product_group_crud.html', {'product_groups': product_group_page,
#                                                        'page_list': product_group_page, 'page_range': page_range, })
#
#
# def product_group_update(request, product_group_id, action_name):
#     if action_name == 'update':
#         product_group = ProductGroup.objects.get(id=product_group_id)
#     elif action_name == 'new':
#         product_group = ''
#
#     if request.method == 'POST':
#         if action_name == 'update':
#             form = ProductGroupForm(request.POST or None, instance=product_group)
#         elif action_name == 'new':
#             form = ProductGroupForm(request.POST)
#
#         if form.is_valid():
#             form.save()
#             return redirect('product_group_crud')
#     else:
#         if action_name == 'update':
#             form = ProductGroupForm(instance=product_group)
#         elif action_name == 'new':
#             form = ProductGroupForm()
#     return render(request, 'product_group_update.html', {'form': form, 'action': action_name})
#
#
# def price_offer_update(request, price_offer_id, task_id):
#     price_offer = PriceOffer.objects.get(pk=price_offer_id)
#     price_offer_item = (PriceOfferItem.objects.filter(price_offer=price_offer).
#                         order_by('product__group__group_name', 'product__name'))
#     price_offer_sum_value = PriceOfferItem.objects.filter(price_offer=price_offer).aggregate(value__sum=Sum(
#         F('amount') * F('price')))
#
#     total_power = PriceOfferItem.objects.filter(price_offer=price_offer, product__group__group_name='2. Napelem') \
#                       .annotate(total_power=F('amount') * F('product__output_power')) \
#                       .aggregate(total_power_sum=Sum('total_power'))['total_power_sum'] or 0
#
#     p = Paginator(price_offer_item, 10)
#     page = request.GET.get('page', 1)
#     price_offer_item_page = p.get_page(page)
#     page_range = p.get_elided_page_range(number=page, on_each_side=2, on_ends=2)
#
#     if request.method == 'POST':
#         item_action = request.POST.get('item_action')
#         if item_action:
#             # Szétválasztjuk az egyedi azonosítót és a művelet nevét
#             item_action_parts = item_action.split('_')
#             item_action_name = item_action_parts[0]
#             price_offer_item_id = item_action_parts[1]
#
#             if item_action_name == 'product':  # Árajánlat tételének Termék kiválasztása
#                 return redirect('price_offer_item_product', price_offer_id=price_offer_id,
#                                 price_offer_item_id=price_offer_item_id, task_id=task_id)
#             elif item_action_name == 'amount':
#                 return redirect('price_offer_item_amount', price_offer_id=price_offer_id,
#                                 price_offer_item_id=price_offer_item_id, task_id=task_id)
#             elif item_action_name == 'price':
#                 return redirect('price_offer_item_price', price_offer_id=price_offer_id,
#                                 price_offer_item_id=price_offer_item_id, task_id=task_id)
#             elif item_action_name == 'delete':
#                 delete_item = PriceOfferItem.objects.get(pk=price_offer_item_id)
#                 delete_item.delete()
#             elif item_action_name == 'new':  # Új árajánlat tételt vesz fel
#                 PriceOfferItem.objects.create(price_offer=price_offer, )
#             elif item_action_name == 'comment':
#                 return redirect('price_offer_comment', price_offer_id=price_offer_id, task_id=task_id)
#             elif item_action_name == 'changemoneyHUF-EUR':
#                 return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
#                                 change='HUF-EUR')
#             elif item_action_name == 'changemoneyHUF-USD':
#                 return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
#                                 change='HUF-USD')
#             elif item_action_name == 'changemoneyEUR-HUF':
#                 return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
#                                 change='EUR-HUF')
#             elif item_action_name == 'changemoneyUSD-HUF':
#                 return redirect('price_offer_change_money', price_offer_id=price_offer_id, task_id=task_id,
#                                 change='USD-HUF')
#             elif item_action_name == 'makepdf':
#                 return redirect('price_offer_makepdf', price_offer_id=price_offer_id, task_id=task_id)
#             elif item_action_name == 'back':
#                 return redirect('p_04_1_elozetes_arajanlatok', task_id=task_id)
#         return redirect(request.path)  # Frissül az oldal
#     return render(request, 'price_offer_update.html',
#                   {'price_offer': price_offer, 'price_offer_items': price_offer_item_page,
#                    'price_offer_sum_value': price_offer_sum_value['value__sum'],
#                    'total_power': total_power,
#                    'page_list': price_offer_item_page, 'page_range': page_range, })
#
#
# def price_offer_item_product(request, price_offer_id, price_offer_item_id, task_id):
#     product_group = ProductGroup.objects.all().order_by('group_name')  # Összes termékcsoport
#     price_offer_item = PriceOfferItem.objects.get(pk=price_offer_item_id)  # A módosítandó árajánlat tétel
#
#     if request.method == 'POST':
#         product_action = request.POST.get('product_action')  # Product.id-vel jön vissza
#         product = Product.objects.get(pk=product_action)  # A kiválasztott termék
#         price_offer_item.product = product  # Árajánlat tételének termék beállítása
#         price_offer_item.price = product.price  # A termék alapértelmezett árának beállítása
#         price_offer_item.save()
#         return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
#     return render(request, 'price_offer_item_product.html',
#                   {'product_groups': product_group, 'price_offer_item': price_offer_item})
#
#
# def price_offer_item_amount(request, price_offer_id, price_offer_item_id, task_id):
#     price_offer_item = PriceOfferItem.objects.get(pk=price_offer_item_id)  # A módosítandó árajánlat tétel
#     product = price_offer_item.product
#     unit_choice = product.get_unit_display()
#
#     if request.method == 'POST':
#         form = PriceOfferItemAmountForm(request.POST or None, instance=price_offer_item)
#         if form.is_valid():
#             form.save()
#             return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
#     else:
#         form = PriceOfferItemAmountForm(instance=price_offer_item)
#
#     return render(request, 'price_offer_item_amount.html',
#                   {'price_offer_item': price_offer_item, 'form': form, 'unit_choice': unit_choice})
#
#
# def price_offer_item_price(request, price_offer_id, price_offer_item_id, task_id):
#     price_offer_item = PriceOfferItem.objects.get(pk=price_offer_item_id)  # A módosítandó árajánlat tétel
#     price_offer = PriceOffer.objects.get(pk=price_offer_id)
#     currency = price_offer.currency
#
#     if request.method == 'POST':
#         form = PriceOfferItemPriceForm(request.POST or None, instance=price_offer_item)
#         if form.is_valid():
#             form.save()
#             return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
#     else:
#         form = PriceOfferItemPriceForm(instance=price_offer_item)
#
#     return render(request, 'price_offer_item_price.html',
#                   {'price_offer_item': price_offer_item, 'form': form, 'currency': currency})
#
#
# def price_offer_comment(request, price_offer_id, task_id):
#     price_offer = PriceOffer.objects.get(pk=price_offer_id)  # A módosítandó árajánlat
#
#     if request.method == 'POST':
#         form = PriceOfferCommentForm(request.POST or None, instance=price_offer)
#         if form.is_valid():
#             form.save()
#             return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
#     else:
#         form = PriceOfferCommentForm(instance=price_offer)
#
#     return render(request, 'price_offer_comment.html',
#                   {'price_offer': price_offer, 'form': form})
#
#
# def price_offer_change_money(request, price_offer_id, task_id, change):
#     price_offer = PriceOffer.objects.get(pk=price_offer_id)  # A módosítandó árajánlat
#
#     if request.method == 'POST':
#         form = PriceOfferChangeForm(request.POST or None, instance=price_offer)
#         if form.is_valid():
#             if change == 'HUF-EUR' or change == 'HUF-USD':
#                 num_updated = (PriceOfferItem.objects.filter(price_offer=price_offer)
#                                .update(price=F('price') / price_offer.change_rating))
#             else:
#                 num_updated = (PriceOfferItem.objects.filter(price_offer=price_offer)
#                                .update(price=F('price') * price_offer.change_rating))
#             if num_updated != 0:
#                 if change == 'HUF-EUR':
#                     price_offer.currency = 'EUR'
#                 elif change == 'HUF-USD':
#                     price_offer.currency = 'USD'
#                 elif change == 'EUR-HUF' or change == 'USD-HUF':
#                     price_offer.currency = 'HUF'
#                 form.save()
#                 messages.success(request, f'Átváltottad az árajánlatot ({change})')
#             else:
#                 messages.success(request, f'Nem sikerült az tételek átváltása ({change})')
#             return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
#     else:
#         form = PriceOfferChangeForm(instance=price_offer)
#
#     return render(request, 'price_offer_change.html',
#                   {'price_offer': price_offer, 'form': form, 'change': change})
#
#
# def price_offer_makepdf(request, price_offer_id, task_id):
#     price_offer = PriceOffer.objects.get(pk=price_offer_id)
#     task = Task.objects.get(pk=task_id)
#
#     pdf_path = os.path.join(settings.MEDIA_ROOT, f'{task.customer.id}',
#                                      f'{price_offer.file_path}')
#     doc = SimpleDocTemplate(pdf_path, pagesize=letter)
#     elements = []
#
#     return redirect('price_offer_update', price_offer_id=price_offer_id, task_id=task_id)
