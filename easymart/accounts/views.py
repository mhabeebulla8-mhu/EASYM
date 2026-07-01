from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, F
from django.db import transaction

from datetime import timedelta

from .models import User, OTPCode, Address
from cart.models import Cart, CartItem # type: ignore
from orders.models import Order

import json
import random
import re


# =========================================================
# HELPERS
# =========================================================

def generate_username(email):
    base = email.split('@')[0]
    username = base
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1

    return username


def is_valid_email(email):
    return bool(
        re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)
    )


def generate_otp():
    return str(random.randint(100000, 999999))


def cleanup_old_otps():
    OTPCode.objects.filter(
        created_at__lt=timezone.now() - timedelta(minutes=10)
    ).delete()


# =========================================================
# SIGNUP
# =========================================================

@csrf_exempt
def signup(request):

    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == "POST":

        # ✅ SUPPORT BOTH FORM + JSON
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
                email = data.get("email", "").lower().strip()
                password = data.get("password", "").strip()
            else:
                email = request.POST.get("email", "").lower().strip()
                password = request.POST.get("password", "").strip()
        except:
            return JsonResponse({"error": "Invalid request"}, status=400)

        # validation
        if not is_valid_email(email):
            return JsonResponse({"error": "Invalid email"}, status=400)

        if len(password) < 6:
            return JsonResponse({"error": "Password too short"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        # Check if OTP was verified
        verified_otp = OTPCode.objects.filter(
            email=email,
            purpose='signup',
            verified=True
        ).order_by('-created_at').first()

        if not verified_otp or verified_otp.is_expired():
            return JsonResponse({"error": "Please verify your email with OTP first"}, status=400)

        try:
            User.objects.create_user(
                username=generate_username(email),
                email=email,
                password=password
            )

            # Clean up the verified OTP
            verified_otp.delete()

            return JsonResponse({
                "success": True,
                "message": "Account created successfully"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'accounts/signup.html')

# =========================================================
# LOGIN PORTAL
# =========================================================

def login_portal(request):

    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/login_portal.html')


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == "POST":

        email = request.POST.get("email", "").lower().strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            messages.error(request, "All fields are required")
            return redirect('accounts:login')

        user_obj = User.objects.filter(email=email).first()

        if not user_obj:
            messages.error(request, "User not found")
            return redirect('accounts:login')

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user:
            login(request, user)

            messages.success(request, "Login successful")

            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)

            if user.is_staff or user.is_superuser:
                return redirect('/admin/')

            return redirect('products:home')

        messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html')


# =========================================================
# LOGOUT
# =========================================================

@login_required(login_url='accounts:login')
def logout_view(request):

    logout(request)

    messages.success(request, "Logged out successfully")

    return redirect('accounts:login')


# =========================================================
# AJAX LOGIN API
# =========================================================

@require_POST
def api_login(request):

    try:
        data = json.loads(request.body)

        email = data.get('email', '').lower().strip()
        password = data.get('password', '').strip()

        user_obj = User.objects.filter(email=email).first()

        if not user_obj:
            return JsonResponse(
                {'error': 'User not found'},
                status=404
            )

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user:
            login(request, user)

            redirect_url = '/admin/' if user.is_staff or user.is_superuser else '/products/home/'
            return JsonResponse({
                'success': True,
                'redirect': redirect_url
            })

        return JsonResponse(
            {'error': 'Invalid credentials'},
            status=401
        )

    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )


# =========================================================
# OTP LOGIN

@require_POST
def otp_login(request):

    try:
        data = json.loads(request.body)

        email = data.get('email', '').lower().strip()
        otp = data.get('otp', '').strip()

        if not is_valid_email(email):
            return JsonResponse({'error': 'Invalid email address'}, status=400)

        if not otp:
            return JsonResponse({'error': 'OTP is required'}, status=400)

        otp_obj = OTPCode.objects.filter(
            email=email,
            code=otp,
            purpose='login'
        ).first()

        if not otp_obj:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)

        if otp_obj.is_expired():
            otp_obj.delete()
            return JsonResponse({'error': 'OTP expired'}, status=400)

        otp_obj.verified = True
        otp_obj.delete()

        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            return JsonResponse({'error': 'User not found'}, status=404)

        login(request, user_obj)

        redirect_url = '/admin/' if user_obj.is_staff or user_obj.is_superuser else '/products/home/'
        return JsonResponse({
            'success': True,
            'redirect': redirect_url
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =========================================================
# SEND OTP
# =========================================================

@csrf_exempt
@require_POST
def send_otp(request):

    try:
        cleanup_old_otps()

        data = json.loads(request.body)

        email = data.get('email', '').lower().strip()
        purpose = data.get('purpose', 'login')

        if not is_valid_email(email):
            return JsonResponse(
                {'error': 'Invalid email address'},
                status=400
            )

        # Rate limiting
        last_otp = OTPCode.objects.filter(
            email=email
        ).order_by('-created_at').first()

        if last_otp and timezone.now() < last_otp.created_at + timedelta(seconds=60):

            return JsonResponse(
                {'error': 'Please wait 60 seconds before requesting another OTP'},
                status=429
            )

        # Remove previous OTPs
        OTPCode.objects.filter(email=email).delete()

        otp = generate_otp()

        OTPCode.objects.create(
            email=email,
            code=otp,
            purpose=purpose
        )

        send_mail(
            subject='EasyMart OTP Verification',
            message=f'''
Your EasyMart OTP is: {otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

- EasyMart Team
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

        return JsonResponse({
            'success': True,
            'message': 'OTP sent successfully'
        })

    except Exception as e:

        return JsonResponse({
            'error': f'Failed to send OTP: {str(e)}'
        }, status=500)


# =========================================================
# VERIFY OTP
# =========================================================

@require_POST
def verify_otp(request):

    try:
        data = json.loads(request.body)

        email = data.get('email', '').lower().strip()
        otp = data.get('otp', '').strip()
        purpose = data.get('purpose', 'login')

        otp_obj = OTPCode.objects.filter(
            email=email,
            code=otp,
            purpose=purpose
        ).first()

        if not otp_obj:
            return JsonResponse({
                'error': 'Invalid OTP'
            }, status=400)

        if otp_obj.is_expired():
            otp_obj.delete()

            return JsonResponse({
                'error': 'OTP expired'
            }, status=400)

        otp_obj.verified = True
        otp_obj.save()

        return JsonResponse({
            'success': True,
            'message': 'OTP verified successfully'
        })

    except Exception as e:

        return JsonResponse({
            'error': str(e)
        }, status=500)


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    return render(
        request,
        'accounts/forgot_password.html'
    )


# =========================================================
# RESET PASSWORD PAGE
# =========================================================

def reset_password_page(request, uidb64, token):

    return render(
        request,
        'accounts/reset_password.html'
    )


# =========================================================
# RESET PASSWORD API
# =========================================================

@require_POST
def reset_password_api(request):

    try:
        data = json.loads(request.body)

        email = data.get("email", "").lower().strip()
        otp = data.get("otp", "").strip()
        new_password = data.get("password", "").strip()

        if len(new_password) < 6:
            return JsonResponse({
                "error": "Password must be at least 6 characters"
            }, status=400)

        user = User.objects.filter(email=email).first()

        if not user:
            return JsonResponse({
                "error": "User not found"
            }, status=404)

        otp_obj = OTPCode.objects.filter(
            email=email,
            code=otp,
            purpose='reset',
            verified=True
        ).first()

        if not otp_obj:
            return JsonResponse({
                "error": "OTP verification required"
            }, status=400)

        if otp_obj.is_expired():
            otp_obj.delete()

            return JsonResponse({
                "error": "OTP expired"
            }, status=400)

        user.set_password(new_password)
        user.save()

        otp_obj.delete()

        return JsonResponse({
            "success": True,
            "message": "Password reset successful"
        })

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


# =========================================================
# DASHBOARD
# =========================================================

@login_required(login_url='accounts:login')
def dashboard(request):

    user = request.user

    orders = Order.objects.filter(
        user=user
    ).order_by('-created_at')

    total_orders = orders.count()

    total_spent = orders.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    recent_orders = orders[:5]

    cart = Cart.objects.filter(user=user).first()

    cart_items = []
    cart_total = 0
    cart_count = 0

    if cart:

        cart_items = CartItem.objects.filter(
            cart=cart
        ).select_related('product')

        cart_total = cart_items.aggregate(
            total=Sum(
                F('quantity') * F('product__price')
            )
        )['total'] or 0

        cart_count = cart_items.aggregate(
            total=Sum('quantity')
        )['total'] or 0

    address = Address.objects.filter(
        user=user,
        is_default=True
    ).first()

    return render(request, 'accounts/dashboard.html', {
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'all_orders': orders,
        'cart_items': cart_items[:5],
        'cart_total': cart_total,
        'cart_count': cart_count,
        'address': address
    })


# =========================================================
# ADDRESS MANAGEMENT
# =========================================================

@login_required(login_url='accounts:login')
def address_list(request):

    addresses = Address.objects.filter(
        user=request.user
    )

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address_line = request.POST.get("address_line", "").strip()
        city = request.POST.get("city", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        if not all([
            full_name,
            phone,
            address_line,
            city,
            pincode
        ]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            is_first_address = not Address.objects.filter(user=request.user).exists()

            address = Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line=address_line,
                city=city,
                pincode=pincode,
                is_default=is_first_address,
            )

            return JsonResponse({
                'success': True,
                'message': 'Address added successfully',
                'address': {
                    'id': address.id,
                    'full_name': address.full_name,
                    'phone': address.phone,
                    'address_line': address.address_line,
                    'city': address.city,
                    'pincode': address.pincode,
                    'is_default': address.is_default,
                },
            })

        except Exception:
            return JsonResponse({'error': 'Failed to add address'}, status=500)

    return render(request, 'accounts/address.html', {
        'addresses': addresses,
        'from_checkout': request.GET.get('next') == 'checkout',
    })


# =========================================================
# SET DEFAULT ADDRESS
# =========================================================

@login_required(login_url='accounts:login')
@require_POST
def set_default_address(request, id):

    try:
        with transaction.atomic():

            Address.objects.filter(
                user=request.user
            ).update(is_default=False)

            address = get_object_or_404(
                Address,
                id=id,
                user=request.user
            )

            address.is_default = True
            address.save()

        return JsonResponse({
            'success': True,
            'message': 'Default address updated successfully'
        })

    except Exception as e:

        return JsonResponse({
            'error': str(e)
        }, status=500)


# =========================================================
# DELETE ADDRESS
# =========================================================

@login_required(login_url='accounts:login')
@require_POST
def delete_address(request, id):

    try:

        address = get_object_or_404(
            Address,
            id=id,
            user=request.user
        )

        address.delete()

        return JsonResponse({
            'success': True,
            'message': 'Address deleted successfully'
        })

    except Exception as e:

        return JsonResponse({
            'error': str(e)
        }, status=500)


# =========================================================
# EDIT ADDRESS
# =========================================================

@login_required(login_url='accounts:login')
def edit_address(request, id):

    address = get_object_or_404(
        Address,
        id=id,
        user=request.user
    )

    if request.method == 'GET':
        return JsonResponse({
            'id': address.id,
            'full_name': address.full_name,
            'phone': address.phone,
            'address_line': address.address_line,
            'city': address.city,
            'pincode': address.pincode
        })

    elif request.method == 'POST':

        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address_line = request.POST.get("address_line", "").strip()
        city = request.POST.get("city", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        if not all([
            full_name,
            phone,
            address_line,
            city,
            pincode
        ]):
            return JsonResponse({
                'error': 'All fields are required'
            }, status=400)

        try:

            address.full_name = full_name
            address.phone = phone
            address.address_line = address_line
            address.city = city
            address.pincode = pincode
            address.save()

            return JsonResponse({
                'success': True,
                'message': 'Address updated successfully'
            })

        except Exception as e:

            return JsonResponse({
                'error': str(e)
            }, status=500)

    return JsonResponse({
        'error': 'Method not allowed'
    }, status=405)