from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from store.models import Product
from .models import Order, OrderItem, DropProduct
from .forms import CheckoutForm
import json


# ---------------------------------------------------------------------------
# CART  (session-based, no DB model needed)
# ---------------------------------------------------------------------------

def _get_cart(request):
    """Return cart dict from session: {product_slug: quantity}"""
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def cart_view(request):
    cart = _get_cart(request)
    items = []
    subtotal = 0

    for slug, qty in cart.items():
        try:
            product = Product.objects.get(slug=slug, is_active=True)
            price = product.display_price or 0
            line_total = price * qty
            subtotal += line_total
            items.append({
                'product': product,
                'quantity': qty,
                'unit_price': price,
                'line_total': line_total,
            })
        except Product.DoesNotExist:
            pass

    return render(request, 'dropshipping/cart.html', {
        'items': items,
        'subtotal': subtotal,
        'total': subtotal,
        'cart_count': sum(cart.values()),
    })


def add_to_cart(request, slug):
    if request.method != 'POST':
        return redirect('cart')

    cart = _get_cart(request)
    qty = int(request.POST.get('quantity', 1))
    cart[slug] = cart.get(slug, 0) + qty
    _save_cart(request, cart)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': sum(cart.values()), 'message': 'Added to cart!'})

    messages.success(request, 'Item added to cart!')
    return redirect('cart')


def remove_from_cart(request, slug):
    cart = _get_cart(request)
    cart.pop(slug, None)
    _save_cart(request, cart)
    return redirect('cart')


def update_cart(request, slug):
    if request.method == 'POST':
        cart = _get_cart(request)
        qty = int(request.POST.get('quantity', 1))
        if qty > 0:
            cart[slug] = qty
        else:
            cart.pop(slug, None)
        _save_cart(request, cart)
    return redirect('cart')


# ---------------------------------------------------------------------------
# CHECKOUT
# ---------------------------------------------------------------------------

def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    # Build cart items for display
    items = []
    subtotal = 0
    shipping_fee = 0
    available_payment_methods = {'cod', 'bank', 'stripe', 'paypal'}

    for slug, qty in cart.items():
        try:
            product = Product.objects.get(slug=slug, is_active=True)
            price = product.display_price or 0
            line_total = price * qty
            subtotal += line_total
            items.append({'product': product, 'quantity': qty,
                          'unit_price': price, 'line_total': line_total})
                          
            if hasattr(product, 'drop_info'):
                drop = product.drop_info
                shipping_fee += (drop.shipping_fee * qty)
                # Intersect payment methods
                product_payments = set()
                if drop.allow_cod: product_payments.add('cod')
                if drop.allow_bank: product_payments.add('bank')
                if drop.allow_stripe: product_payments.add('stripe')
                if drop.allow_paypal: product_payments.add('paypal')
                available_payment_methods.intersection_update(product_payments)
        except Product.DoesNotExist:
            pass

    total = subtotal + shipping_fee

    if request.method == 'POST':
        form = CheckoutForm(request.POST, available_payment_methods=list(available_payment_methods))
        if form.is_valid():
            d = form.cleaned_data
            
            # Escape strings for backend security
            from django.utils.html import escape
            first_name = escape(d['first_name'])
            last_name = escape(d['last_name'])
            email = escape(d['email'])
            phone = escape(d['phone'])
            address_line1 = escape(d['address_line1'])
            address_line2 = escape(d['address_line2'])
            city = escape(d['city'])
            state = escape(d['state'])
            country = escape(d['country'])
            postal_code = escape(d['postal_code'])
            delivery_notes = escape(d['delivery_notes'])
            gate_code = escape(d['gate_code'])
            
            order = Order.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                delivery_notes=delivery_notes,
                leave_at_front_door=d['leave_at_front_door'],
                call_before_delivery=d['call_before_delivery'],
                gate_code=gate_code,
                payment_method=d['payment_method'],
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                total_price=total,
                status='pending',
            )
            # Create order items
            for item in items:
                product = item['product']
                try:
                    drop = product.drop_info
                    s_url = drop.supplier_url
                    s_cost = drop.supplier_cost
                except Exception:
                    s_url = ''
                    s_cost = None

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_title=product.title,
                    product_image=product.image_url,
                    supplier_url=s_url,
                    supplier_cost=s_cost,
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                )

            # Clear cart and save order to session for security
            request.session['cart'] = {}
            request.session['last_order'] = order.order_number
            request.session.modified = True

            if d['payment_method'] == 'stripe':
                return redirect('paymentsystem:process', order_number=order.order_number)

            return redirect('order_success', order_number=order.order_number)
    else:
        form = CheckoutForm(available_payment_methods=list(available_payment_methods), initial={'country': 'Pakistan'})

    return render(request, 'dropshipping/checkout.html', {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total': total,
    })


# ---------------------------------------------------------------------------
# ORDER SUCCESS
# ---------------------------------------------------------------------------

def order_success(request, order_number):
    if request.session.get('last_order') != order_number:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")
        
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'dropshipping/order_success.html', {'order': order})


# ---------------------------------------------------------------------------
# ORDER TRACKING
# ---------------------------------------------------------------------------

import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.html import escape

def order_tracking(request):
    order = None
    searched = False
    error_msg = None

    # Limit length to prevent long payload attacks
    raw_order_number = request.GET.get('order_number', '')[:50].strip()
    raw_email = request.GET.get('email', '')[:100].strip()
    
    # Escape inputs to prevent Reflected XSS when repopulating the form
    safe_order_number = escape(raw_order_number)
    safe_email = escape(raw_email)
    
    if raw_order_number and raw_email:
        searched = True
        is_valid = True
        
        # 1. Strict Regex Validation for Order Number (e.g., ORD-12345678)
        if not re.match(r'^ORD-\d{6,20}$', raw_order_number):
            error_msg = "Invalid order number format. It should start with ORD- followed by numbers."
            is_valid = False
            
        # 2. Strict Email Format Validation
        if is_valid:
            try:
                validate_email(raw_email)
            except ValidationError:
                error_msg = "Please enter a valid email address."
                is_valid = False
                
        # 3. Database Lookup (Django ORM inherently prevents SQL Injection here)
        if is_valid:
            try:
                order = Order.objects.get(order_number=raw_order_number, email__iexact=raw_email)
            except Order.DoesNotExist:
                order = None

    return render(request, 'dropshipping/order_tracking.html', {
        'order': order,
        'searched': searched,
        'error_msg': error_msg,
        'input_order_number': safe_order_number,
        'input_email': safe_email,
    })
