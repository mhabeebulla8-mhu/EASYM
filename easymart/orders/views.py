from decimal import Decimal
import json
import logging
import threading
import time

import razorpay
from razorpay.errors import SignatureVerificationError

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import Address
from cart.models import Cart, CartItem
from products.models import Product
from .models import Order, OrderItem


# =========================================
# ✅ LOGGER
# =========================================
logger = logging.getLogger(__name__)


# =========================================
# ✅ RAZORPAY CLIENT
# =========================================
try:
    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )
except Exception as e:
    logger.error(f"Razorpay initialization failed: {e}")
    client = None


# =========================================
# ✅ AUTO STATUS UPDATE
# =========================================
def auto_update_order_status(order_id):
    statuses = [
        'confirmed',
        'packed',
        'out_for_delivery',
        'delivered'
    ]

    for status in statuses:
        time.sleep(60)  # Changed from 5 seconds to 60 seconds (1 minute per step)

        try:
            order = Order.objects.get(id=order_id)

            if order.status in ['delivered', 'cancelled']:
                break

            order.status = status
            order.save(update_fields=['status'])

        except Order.DoesNotExist:
            break


# =========================================
# ✅ CHECKOUT PAGE
# =========================================
@login_required(login_url='accounts:login')
def checkout(request):

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect('cart:cart_view')

    items = CartItem.objects.filter(
        cart=cart
    ).select_related('product')

    if not items.exists():
        messages.error(request, "Your cart is empty")
        return redirect('cart:cart_view')

    total = Decimal('0.00')

    for item in items:
        total += Decimal(str(item.product.discounted_price)) * item.quantity

    address = Address.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    return render(request, 'orders/checkout.html', {
        'items': items,
        'total': total,
        'address': address,
    })


# =========================================
# ✅ CREATE RAZORPAY ORDER
# =========================================
@login_required(login_url='accounts:login')
def create_razorpay_order(request):

    if not client:
        return JsonResponse({
            "error": "Payment service unavailable"
        }, status=503)

    try:
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return JsonResponse({
                "error": "Cart is empty"
            }, status=400)

        items = CartItem.objects.filter(
            cart=cart
        ).select_related('product')

        if not items.exists():
            return JsonResponse({
                "error": "Cart is empty"
            }, status=400)

        total = Decimal('0.00')

        for item in items:
            total += Decimal(str(item.product.discounted_price)) * item.quantity

        amount = int(total * 100)

        razorpay_order = client.order.create({  # type: ignore[attr-defined]
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        logger.info(
            f"Razorpay order created for user {request.user.id}"
        )

        return JsonResponse({
            "order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "key": settings.RAZORPAY_KEY_ID
        })

    except Exception as e:
        logger.error(f"Create Razorpay order error: {e}")

        return JsonResponse({
            "error": "Unable to create payment order"
        }, status=500)


# =========================================
# ✅ VERIFY PAYMENT
# =========================================
@csrf_exempt
@require_POST
@login_required(login_url='accounts:login')
def verify_payment(request):

    if not client:
        return JsonResponse({
            "status": "service_unavailable"
        }, status=503)

    try:
        data = json.loads(request.body)

        params_dict = {
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature"),
        }

        client.utility.verify_payment_signature(params_dict)  # type: ignore[attr-defined]
        logger.info(f"Payment verified for user {request.user.id}")

        # ✅ IMPORTANT FIX: directly return real function result
        return create_final_order_logic(request)

    except SignatureVerificationError:
        logger.error("Payment signature verification failed")

        return JsonResponse({
            "status": "verification_failed"
        }, status=400)

    except Exception as e:
        logger.error(f"Verify payment error: {e}")

        return JsonResponse({
            "status": "failed"
        }, status=500)

# =========================================
# ✅ CREATE FINAL ONLINE ORDER
# =========================================
@transaction.atomic
def create_final_order_logic(request):

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        return JsonResponse({"status": "cart_missing"}, status=400)

    items = CartItem.objects.filter(cart=cart).select_related('product')

    if not items.exists():
        return JsonResponse({"status": "cart_empty"}, status=400)

    address = Address.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    if not address:
        return JsonResponse({"status": "no_address"}, status=400)

    try:

        total = Decimal('0.00')
        order_items = []

        # STOCK CHECK
        for item in items:
            if item.quantity > item.product.stock:
                return JsonResponse({
                    "status": "out_of_stock",
                    "product": item.product.name
                }, status=400)

            total += item.product.discounted_price * item.quantity

        # CREATE ORDER
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            address=address.address_line,
            city=address.city,
            payment_method='online',
            payment_status='paid',
            status='confirmed'
        )

        # ORDER ITEMS
        for item in items:

            order_items.append(OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price
            ))

            item.product.stock -= item.quantity
            item.product.save(update_fields=['stock'])

        OrderItem.objects.bulk_create(order_items)

        # CLEAR CART
        items.delete()

        # AUTO STATUS THREAD
        threading.Thread(
            target=auto_update_order_status,
            args=(order.pk,),
            daemon=True
        ).start()

        return JsonResponse({
            "status": "success",
            "order_id": order.pk
        })

    except Exception as e:
        logger.error(f"Order creation error: {e}")

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    
# =========================================
# ✅ PLACE COD ORDER
# =========================================
@require_POST
@login_required(login_url='accounts:login')
@transaction.atomic
def place_cod_order(request):

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        return JsonResponse({
            "status": "cart_empty"
        }, status=400)

    items = CartItem.objects.filter(
        cart=cart
    ).select_related('product')

    if not items.exists():
        return JsonResponse({
            "status": "cart_empty"
        }, status=400)

    address = Address.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    if not address:
        return JsonResponse({
            "status": "no_address"
        }, status=400)

    try:

        total = Decimal('0.00')
        order_items = []

        # =====================================
        # ✅ STOCK CHECK
        # =====================================
        for item in items:

            if item.quantity > item.product.stock:
                return JsonResponse({
                    "status": "out_of_stock",
                    "product": item.product.name
                }, status=400)

            total += Decimal(str(item.product.discounted_price)) * item.quantity

        # =====================================
        # ✅ CREATE ORDER
        # =====================================
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            address=address.address_line,
            city=address.city,
            payment_method='cod',
            payment_status='pending',
            status='confirmed'
        )

        # =====================================
        # ✅ CREATE ORDER ITEMS
        # =====================================
        for item in items:

            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.discounted_price
                )
            )

            # reduce stock
            item.product.stock -= item.quantity
            item.product.save(update_fields=['stock'])

        OrderItem.objects.bulk_create(order_items)

        # =====================================
        # ✅ CLEAR CART
        # =====================================
        items.delete()

        # =====================================
        # ✅ AUTO STATUS THREAD
        # =====================================
        threading.Thread(
            target=auto_update_order_status,
            args=(order.pk,),
            daemon=True
        ).start()

        logger.info(
            f"COD order created successfully: #{order.pk}"
        )

        return JsonResponse({
            "status": "success",
            "order_id": order.pk
        })

    except Exception as e:
        logger.error(f"COD order error: {e}")

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


# =========================================
# ✅ SUCCESS PAGE
# =========================================
@login_required(login_url='accounts:login')
def success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'orders/success.html', {
        'order': order
    })


# =========================================
# ✅ ORDER HISTORY
# =========================================
@login_required(login_url='accounts:login')
def history(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        'items',
        'items__product'
    ).order_by('-created_at')

    return render(request, 'orders/history.html', {
        'orders': orders
    })


# =========================================
# ✅ ORDER DETAIL
# =========================================
@login_required(login_url='accounts:login')
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    items = OrderItem.objects.filter(
        order=order
    ).select_related('product')

    return render(request, 'orders/detail.html', {
        'order': order,
        'items': items
    })


# =========================================
# ✅ TRACK ORDER
# =========================================
@login_required(login_url='accounts:login')
def track_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'orders/track.html', {
        'order': order
    })