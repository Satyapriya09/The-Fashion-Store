import json

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Contact, Order, OrderUpdate, Product



def index(request):
    allprods = []
    cats = Product.objects.order_by('category').values_list('category', flat=True).distinct()
    for cat in cats:
        products = Product.objects.filter(category=cat).order_by('-add_date', 'id')
        allprods.append((cat, products))
    params = {
        'allprods': allprods,
        'featured_product': Product.objects.order_by('-add_date', 'id').first(),
    }
    return render(request, 'Shop/index.html', params)


def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query)
            | Q(category__icontains=query)
            | Q(sub_catgory__icontains=query)
        ).order_by('category', 'product_name')
    return render(request, 'Shop/Search.html', {'query': query, 'products': products})


def productview(request , myid):
    product = get_object_or_404(Product, id=myid)
    return render(request, 'Shop/Productview.html', {'product': product})


def checkout(request):
    context = {}
    if request.method == "POST":
        try:
            submitted_items = json.loads(request.POST.get('itemsJson', '{}'))
            if not isinstance(submitted_items, dict) or not submitted_items:
                raise ValueError

            quantities = {}
            for key, value in submitted_items.items():
                if not key.startswith('pr') or not key[2:].isdigit() or len(key) > 12:
                    raise ValueError
                if not isinstance(value, list) or not value:
                    raise ValueError
                quantity = int(value[0])
                if quantity < 1 or quantity > 99:
                    raise ValueError
                quantities[int(key[2:])] = quantity

            required_fields = ('name', 'email', 'address1', 'city', 'state', 'zip_code', 'phone')
            if any(not request.POST.get(field, '').strip() for field in required_fields):
                raise ValueError

            products = {
                product.id: product
                for product in Product.objects.filter(id__in=quantities)
            }
            if len(products) != len(quantities):
                raise ValueError

            cart = {
                f'pr{product_id}': [quantity, products[product_id].product_name, products[product_id].price]
                for product_id, quantity in quantities.items()
            }
            amount = sum(products[product_id].price * quantity for product_id, quantity in quantities.items())
            with transaction.atomic():
                order = Order.objects.create(
                    items_json=json.dumps(cart),
                    name=request.POST.get('name', '').strip(),
                    email=request.POST.get('email', '').strip(),
                    address=' '.join(filter(None, [request.POST.get('address1', '').strip(), request.POST.get('address2', '').strip()])),
                    city=request.POST.get('city', '').strip(),
                    state=request.POST.get('state', '').strip(),
                    zip_code=request.POST.get('zip_code', '').strip(),
                    phone=request.POST.get('phone', '').strip(),
                    amount=amount,
                )
                OrderUpdate.objects.create(order_id=order.order_id, update_desc="The order has been placed")
            return render(request, 'Shop/Checkout.html', {'thank': True, 'id': order.order_id})
        except (ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError):
            context['checkout_error'] = 'Your bag could not be checked. Please review it and try again.'
    return render(request, 'Shop/Checkout.html', context)


def about(request):
    return render(request, 'Shop/About.html')


def contact(request):
    sent = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        if name.strip() and email.strip() and desc.strip():
            Contact.objects.create(name=name, email=email, phone=phone, desc=desc)
            sent = True
    return render(request, 'Shop/Contact.html', {'sent': sent})


def trackorder(request, ):
    if request.method=="POST":
        order_id = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        order = Order.objects.filter(order_id=order_id, email=email).first() if order_id.isdigit() else None
        updates = []
        items = []
        if order:
            updates = [
                {'text': update.update_desc, 'time': update.timestamp}
                for update in OrderUpdate.objects.filter(order_id=order_id).order_by('timestamp', 'update_id')
            ]
            try:
                items = json.loads(order.items_json)
            except json.JSONDecodeError:
                items = []
        return JsonResponse({'found': order is not None, 'updates': updates, 'items': items})

    return render(request, 'Shop/Track_Order.html')