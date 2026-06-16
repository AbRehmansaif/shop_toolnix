import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dropshipping.models import Order
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_process(request, order_number):
    if request.session.get('last_order') != order_number:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")
        
    order = get_object_or_404(Order, order_number=order_number)
    
    # Check if payment is already made
    if order.payment_status == 'paid':
        return redirect('order_success', order_number=order.order_number)
        
    if request.method == 'POST':
        # This will be called by AJAX from Stripe Elements
        pass
        
    # We will use Stripe Elements, so we need to create a PaymentIntent
    # amount in cents
    amount = int(order.total_price * 100)
    
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='usd',
        metadata={'order_number': order.order_number}
    )
    
    context = {
        'order': order,
        'client_secret': intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'paymentsystem/process.html', context)

def payment_success(request, order_number):
    if request.session.get('last_order') != order_number:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")
        
    order = get_object_or_404(Order, order_number=order_number)
    # The actual order status will be updated via the webhook
    # But we can show a success page and maybe check the intent status
    return redirect('order_success', order_number=order.order_number)

def payment_cancelled(request, order_number):
    if request.session.get('last_order') != order_number:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")
        
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'paymentsystem/cancelled.html', {'order': order})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event or payment_intent.succeeded
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        order_number = intent.get('metadata', {}).get('order_number')
        
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
                # Strict amount verification
                intent_amount = intent.get('amount_received', 0)
                expected_amount = int(order.total_price * 100)
                
                if intent_amount == expected_amount:
                    order.payment_status = 'paid'
                    if order.status == 'pending':
                        order.status = 'processing'
                else:
                    # Potential hijacking or error
                    order.payment_status = 'failed'
                    order.admin_notes += f"\n[SECURITY WARNING] Payment amount mismatch. Expected {expected_amount}, got {intent_amount}."
                
                order.save()
            except Order.DoesNotExist:
                pass

    return HttpResponse(status=200)
