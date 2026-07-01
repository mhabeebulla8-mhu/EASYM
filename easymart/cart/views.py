from decimal import Decimal
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product # type: ignore
from .models import Cart, CartItem


# =========================================
# ✅ COMMON JSON PARSER
# =========================================
def parse_request_data(request):
    try:
        if request.body:
            return json.loads(request.body)
    except json.JSONDecodeError:
        pass

    return request.POST


# =========================================
# ✅ GET CART COUNT
# =========================================
def get_cart_count(cart):
    return (
        CartItem.objects.filter(cart=cart).aggregate(
            total=Sum('quantity')
        )['total']
        or 0
    )


# =========================================
# 🛒 VIEW CART PAGE
# =========================================
@login_required(login_url='accounts:login')
def cart_view(request):

    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = CartItem.objects.filter(
        cart=cart
    ).select_related('product')

    total = Decimal('0.00')

    for item in items:
        total += item.product.discounted_price * item.quantity

    return render(request, 'cart/cart.html', {
        'items': items,
        'total': total,
    })


# =========================================
# ➕ ADD TO CART
# =========================================
@require_POST
def add_to_cart(request):

    data = parse_request_data(request)

    product_id = data.get('product_id')

    if not product_id:
        return JsonResponse({
            "success": False,
            "error": "Product ID missing"
        }, status=400)

    product = get_object_or_404(Product, pk=product_id)

    # =====================================
    # ✅ AUTHENTICATED USER
    # =====================================
    if request.user.is_authenticated:

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:

            if item.quantity >= product.stock:
                return JsonResponse({
                    "success": False,
                    "error": "Stock limit reached"
                }, status=400)

            item.quantity += 1
            item.save(update_fields=['quantity'])

        quantity = item.quantity
        cart_count = get_cart_count(cart)

    # =====================================
    # ✅ GUEST USER
    # =====================================
    else:

        guest_cart = request.session.get('guest_cart', {})
        pid = str(product_id)

        current_qty = guest_cart.get(pid, 0)

        if current_qty >= product.stock:
            return JsonResponse({
                "success": False,
                "error": "Stock limit reached"
            }, status=400)

        guest_cart[pid] = current_qty + 1

        request.session['guest_cart'] = guest_cart
        request.session.modified = True

        quantity = guest_cart[pid]
        cart_count = sum(guest_cart.values())

    return JsonResponse({
        "success": True,
        "product_id": product.pk,
        "quantity": quantity,
        "cart_count": cart_count
    })


# =========================================
# ➕➖ UPDATE CART
# =========================================
@require_POST
def update_cart(request):

    data = parse_request_data(request)

    product_id = data.get('product_id')
    action = data.get('action')

    if not product_id or action not in ['increase', 'decrease']:

        return JsonResponse({
            "success": False,
            "error": "Invalid request"
        }, status=400)

    product = get_object_or_404(Product, pk=product_id)

    # =====================================
    # ✅ AUTHENTICATED USER
    # =====================================
    if request.user.is_authenticated:

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

        item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        if not item:
            return JsonResponse({
                "success": False,
                "error": "Item not found"
            }, status=404)

        # ==============================
        # INCREASE
        # ==============================
        if action == "increase":

            if item.quantity >= product.stock:
                return JsonResponse({
                    "success": False,
                    "error": "Stock limit reached"
                }, status=400)

            item.quantity += 1
            item.save(update_fields=['quantity'])

        # ==============================
        # DECREASE
        # ==============================
        elif action == "decrease":

            item.quantity -= 1

            if item.quantity <= 0:
                item.delete()
                quantity = 0
            else:
                item.save(update_fields=['quantity'])
                quantity = item.quantity

        quantity = quantity if 'quantity' in locals() else item.quantity

        items = CartItem.objects.filter(
            cart=cart
        ).select_related('product')

        total = Decimal('0.00')

        for cart_item in items:
            total += cart_item.product.discounted_price * cart_item.quantity

        cart_count = get_cart_count(cart)

    # =====================================
    # ✅ GUEST USER
    # =====================================
    else:

        guest_cart = request.session.get('guest_cart', {})
        pid = str(product_id)

        if pid not in guest_cart:

            return JsonResponse({
                "success": False,
                "error": "Item not found"
            }, status=404)

        if action == "increase":

            if guest_cart[pid] >= product.stock:
                return JsonResponse({
                    "success": False,
                    "error": "Stock limit reached"
                }, status=400)

            guest_cart[pid] += 1

        elif action == "decrease":

            guest_cart[pid] -= 1

            if guest_cart[pid] <= 0:
                del guest_cart[pid]
                quantity = 0
            else:
                quantity = guest_cart[pid]

        quantity = quantity if 'quantity' in locals() else guest_cart.get(pid, 0)

        request.session['guest_cart'] = guest_cart
        request.session.modified = True

        cart_count = sum(guest_cart.values())
        total = Decimal('0.00')

    return JsonResponse({
        "success": True,
        "product_id": product.pk,
        "quantity": quantity,
        "cart_count": cart_count,
        "total": float(total)
    })


# =========================================
# ❌ REMOVE ITEM (PAGE)
# =========================================
@login_required(login_url='accounts:login')
def remove_from_cart(request, id):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=id,
        cart=cart
    )

    item.delete()

    return redirect('cart:cart_view')


# =========================================
# ❌ REMOVE ITEM (AJAX)
# =========================================
@require_POST
def remove_from_cart_ajax(request):

    data = parse_request_data(request)

    product_id = data.get('product_id')

    if not product_id:

        return JsonResponse({
            "success": False,
            "error": "Product ID missing"
        }, status=400)

    # =====================================
    # ✅ AUTHENTICATED USER
    # =====================================
    if request.user.is_authenticated:

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

        CartItem.objects.filter(
            cart=cart,
            product_id=product_id
        ).delete()

        cart_count = get_cart_count(cart)

    # =====================================
    # ✅ GUEST USER
    # =====================================
    else:

        guest_cart = request.session.get('guest_cart', {})

        pid = str(product_id)

        if pid in guest_cart:
            del guest_cart[pid]

        request.session['guest_cart'] = guest_cart
        request.session.modified = True

        cart_count = sum(guest_cart.values())

    return JsonResponse({
        "success": True,
        "cart_count": cart_count
    })