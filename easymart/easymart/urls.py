from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from products import views as product_views


urlpatterns = [

    # 🔐 Admin
    path('admin/', admin.site.urls),

    # 🏠 Landing Page
    path('', product_views.landing_page, name='landing'),

    # 📦 Apps
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),

]


# ============================
# 🖼 MEDIA FILES (DEV ONLY)
# ============================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)