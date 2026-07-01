from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [

    # 🛒 CHECKOUT PAGE
    path('checkout/', views.checkout, name='checkout'),

    # 💳 RAZORPAY (API)
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),

    # 💵 CASH ON DELIVERY (API)
    path('place-cod-order/', views.place_cod_order, name='place_cod_order'),

    # 🎉 SUCCESS PAGE
    path('success/<int:order_id>/', views.success, name='success'),

    # 📜 ORDER HISTORY
    path('history/', views.history, name='history'),

    # 📄 ORDER DETAIL
    path('detail/<int:order_id>/', views.order_detail, name='detail'),

    # 📦 ORDER TRACKING
    path('track/<int:order_id>/', views.track_order, name='track'),
]