from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.text import slugify

from cart.models import Cart, CartItem
from .models import Category, Offer, Product



# ======================================================
# ✅ SAMPLE PRODUCTS
# ======================================================

SAMPLE_PRODUCTS = [
    {"name": "Apple", "category": "Fruits", "price": 120, "stock": 50, "weight": "500g"},
    {"name": "Banana", "category": "Fruits", "price": 60, "stock": 40, "weight": "1kg"},
    {"name": "Mango", "category": "Fruits", "price": 150, "stock": 30, "weight": "1kg"},
    {"name": "Orange", "category": "Fruits", "price": 80, "stock": 25, "weight": "500g"},

    {"name": "Carrot", "category": "Vegetables", "price": 40, "stock": 35, "weight": "500g"},
    {"name": "Tomato", "category": "Vegetables", "price": 50, "stock": 30, "weight": "1kg"},
    {"name": "Onion", "category": "Vegetables", "price": 45, "stock": 50, "weight": "1kg"},
    {"name": "Potato", "category": "Vegetables", "price": 35, "stock": 60, "weight": "1kg"},

    {"name": "Milk", "category": "Dairy", "price": 55, "stock": 25, "weight": "500ml"},
    {"name": "Butter", "category": "Dairy", "price": 110, "stock": 20, "weight": "200g"},
    {"name": "Cheese", "category": "Dairy", "price": 180, "stock": 15, "weight": "200g"},
    {"name": "Curd", "category": "Dairy", "price": 40, "stock": 20, "weight": "500g"},

    {"name": "Bread", "category": "Bakery", "price": 40, "stock": 25, "weight": "400g"},
    {"name": "Cake", "category": "Bakery", "price": 250, "stock": 10, "weight": "500g"},
    {"name": "Bun", "category": "Bakery", "price": 30, "stock": 20, "weight": "200g"},
    {"name": "Croissant", "category": "Bakery", "price": 60, "stock": 15, "weight": "150g"},

    {"name": "Orange Juice", "category": "Beverages", "price": 80, "stock": 20, "weight": "1L"},
    {"name": "Tea", "category": "Beverages", "price": 120, "stock": 15, "weight": "250g"},
    {"name": "Coffee", "category": "Beverages", "price": 200, "stock": 10, "weight": "200g"},
    {"name": "Cold Drink", "category": "Beverages", "price": 90, "stock": 25, "weight": "1L"},

    {"name": "Chips", "category": "Snacks", "price": 30, "stock": 60, "weight": "100g"},
    {"name": "Biscuits", "category": "Snacks", "price": 25, "stock": 70, "weight": "150g"},
    {"name": "Namkeen", "category": "Snacks", "price": 50, "stock": 40, "weight": "200g"},
    {"name": "Popcorn", "category": "Snacks", "price": 70, "stock": 30, "weight": "150g"},
]


# ======================================================
# CREATE SAMPLE DATA (SAFE FIX)
# ======================================================

def ensure_sample_products():

    # ❌ FIX: Prevent re-running logic every request
    if not Product.objects.exists():
        for item in SAMPLE_PRODUCTS:
            category_name = item["category"]
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"slug": slugify(category_name)}
            )
            Product.objects.create(
                category=category,
                name=item["name"],
                price=item["price"],
                stock=item["stock"],
                weight=item["weight"],
                description="Fresh and high quality product"
            )

    if not Offer.objects.exists():
        import os
        from django.core.files import File
        from django.conf import settings
        
        offers_data = [
            {"title": "Fresh Fruits Special", "subtitle": "Up to 20% OFF on organic fruits", "image_name": "apple.jpg", "category": "Fruits"},
            {"title": "Dairy Delights", "subtitle": "Farm fresh milk delivered daily", "image_name": "milk.jpg", "category": "Dairy"},
            {"title": "Snack Time!", "subtitle": "Buy 1 Get 1 Free on snacks", "image_name": "chips.jpg", "category": "Snacks"},
            {"title": "Bakery Bonanza", "subtitle": "Freshly baked cakes and breads", "image_name": "cake.jpg", "category": "Bakery"},
        ]
        
        for item in offers_data:
            category, _ = Category.objects.get_or_create(name=item["category"])
            offer = Offer(
                title=item["title"],
                subtitle=item["subtitle"],
                category=category,
                is_active=True
            )
            
            img_path = os.path.join(settings.BASE_DIR, 'static', 'images', item["image_name"])
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    offer.image.save(item["image_name"], File(f), save=False)
                    
            offer.save()


# ======================================================
# HOME PAGE (FIXED DISCOUNT + REFRESH ISSUE)
# ======================================================

def home(request):

    ensure_sample_products()

    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    # ==================================================
    # IMPORTANT FIX:
    # FORCE fresh DB fetch every request
    # ==================================================

    products = Product.objects.select_related('category').all()

    # FILTER AVAILABLE
    products = products.filter(available=True)

    # CATEGORY FILTER
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # SEARCH FILTER
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 🔥 FIX: Always show latest updated products first
    products = products.order_by('-updated_at')

    # ==================================================
    # CATEGORIES
    # ==================================================
    categories = Category.objects.all().order_by('name')

    # ==================================================
    # OFFERS (FIXED CLEAN FILTER)
    # ==================================================
    now = timezone.now()

    offers = Offer.objects.filter(
        is_active=True
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    ).select_related('category').order_by('order')

    # ==================================================
    # CART SYNC
    # ==================================================
    cart_items = {}

    if request.user.is_authenticated:

        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            items = CartItem.objects.filter(cart=cart).values(
                'product_id', 'quantity'
            )

            cart_items = {
                item['product_id']: item['quantity']
                for item in items
            }

    else:
        guest_cart = request.session.get('guest_cart', {})

        cart_items = {
            int(k): v for k, v in guest_cart.items()
        }

    # ==================================================
    # CONTEXT
    # ==================================================
    return render(request, 'index.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'cart_items': cart_items,
        'offers': offers,
    })


# ======================================================
# LANDING PAGE
# ======================================================

def landing_page(request):
    return home(request)


# ======================================================
# PRODUCT DETAIL (FIXED QUERY SAFETY)
# ======================================================

def product_detail(request, id):

    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=id
    )

    return render(request, 'products/product.html', {
        'product': product
    })


# ======================================================
# CATEGORY PAGE
# ======================================================

def category_view(request):

    categories = Category.objects.all().order_by('name')

    return render(request, 'products/category.html', {
        'categories': categories
    })