from .models import Cart, CartItem
from django.db.models import Sum

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = CartItem.objects.filter(cart=cart).aggregate(
                total=Sum('quantity')
            )['total'] or 0
        else:
            count = 0
    else:
        cart = request.session.get('guest_cart', {})
        count = sum(cart.values())

    return {
        'cart_count': count
    }