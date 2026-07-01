from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [

    # ======================================================
    # AUTHENTICATION
    # ======================================================

    path(
        'signup/',
        views.signup,
        name='signup'
    ),

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'login-portal/',
        views.login_portal,
        name='login_portal'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # ======================================================
    # DASHBOARD
    # ======================================================

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    # ======================================================
    # OTP APIs
    # ======================================================

    path(
        'api/send-otp/',
        views.send_otp,
        name='send_otp'
    ),

    path(
        'api/verify-otp/',
        views.verify_otp,
        name='verify_otp'
    ),

    path(
        'api/login/',
        views.api_login,
        name='api_login'
    ),

    path(
        'api/otp-login/',
        views.otp_login,
        name='otp_login'
    ),

    # ======================================================
    # PASSWORD RESET
    # ======================================================

    path(
        'forgot-password/',
        views.forgot_password,
        name='forgot_password'
    ),

    path(
        'reset/<uidb64>/<token>/',
        views.reset_password_page,
        name='reset_page'
    ),

    path(
        'reset-api/',
        views.reset_password_api,
        name='reset_api'
    ),

    # ======================================================
    # ADDRESS MANAGEMENT
    # ======================================================

    path(
        'address/',
        views.address_list,
        name='address'
    ),

    path(
        'address/edit/<int:id>/',
        views.edit_address,
        name='edit_address'
    ),

    path(
        'address/default/<int:id>/',
        views.set_default_address,
        name='set_default_address'
    ),

    path(
        'address/delete/<int:id>/',
        views.delete_address,
        name='delete_address'
    ),
]