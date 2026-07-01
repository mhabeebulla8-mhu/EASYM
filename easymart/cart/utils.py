from products.models import Product

from .models import Cart, CartItem


def merge_guest_cart(request, user):
    guest_cart = request.session.get('guest_cart')
    if not guest_cart:
        return

    cart, _ = Cart.objects.get_or_create(user=user)

    for product_id, quantity in guest_cart.items():
        try:
            qty = int(quantity)
            product = Product.objects.get(pk=int(product_id))
        except (Product.DoesNotExist, ValueError, TypeError):
            continue

        if qty <= 0:
            continue

        qty = min(qty, product.stock)
        if qty <= 0:
            continue

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': qty},
        )

        if not created:
            item.quantity = min(item.quantity + qty, product.stock)
            item.save(update_fields=['quantity'])

    del request.session['guest_cart']
    request.session.modified = True
