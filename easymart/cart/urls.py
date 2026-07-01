from django.urls import path

from . import views

app_name = 'cart'


urlpatterns = [

    # =====================================
    # 🛒 CART PAGE
    # =====================================
    path(
        '',
        views.cart_view,
        name='cart_view'
    ),

    # =====================================
    # ➕ ADD TO CART (AJAX)
    # =====================================
    path(
        'add/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    # =====================================
    # ➕➖ UPDATE CART QUANTITY (AJAX)
    # =====================================
    path(
        'update/',
        views.update_cart,
        name='update_cart'
    ),

    # =====================================
    # ❌ REMOVE ITEM (NORMAL)
    # =====================================
    path(
        'remove/<int:id>/',
        views.remove_from_cart,
        name='remove'
    ),

    # =====================================
    # ❌ REMOVE ITEM (AJAX)
    # =====================================
    path(
        'remove-ajax/',
        views.remove_from_cart_ajax,
        name='remove_ajax'
    ),
]