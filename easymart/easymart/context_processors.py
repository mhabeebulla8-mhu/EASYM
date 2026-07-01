from cart.models import Cart, CartItem
from django.db.models import Sum

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            return {
                'cart_count': CartItem.objects.filter(cart=cart).aggregate(
                    total=Sum('quantity')
                )['total'] or 0
            }
    return {'cart_count': 0}