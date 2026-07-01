# 🛒 EasyMart - Grocery Delivery Platform

A modern Django-based grocery delivery application with user authentication, product management, shopping cart, and Razorpay payment integration.

## ✨ Features

### User Management
- ✅ Email-based authentication
- ✅ OTP verification (5-minute expiry)
- ✅ User dashboard with order history
- ✅ Address management with default address
- ✅ Password reset via OTP
- ✅ Profile management

### Product Management
- ✅ Category-based product filtering
- ✅ Advanced search functionality
- ✅ Product discounts with auto-calculation
- ✅ Stock management
- ✅ Product availability tracking
- ✅ Hero banners and offers

### Shopping Cart
- ✅ Add/remove items from cart
- ✅ Quantity adjustment
- ✅ Real-time cart updates (AJAX)
- ✅ Guest cart support (session-based)
- ✅ Auto price calculation with discounts

### Checkout & Payments
- ✅ Multiple payment methods (Online & COD)
- ✅ Razorpay payment gateway integration
- ✅ Order status tracking
- ✅ Auto order status updates
- ✅ Order history with details
- ✅ Payment verification

### Admin Panel
- ✅ Custom admin interface (Jazzmin)
- ✅ Product/category management
- ✅ Order management with bulk actions
- ✅ User management
- ✅ Order status updates
- ✅ Order item tracking

## 🛠️ Tech Stack

- **Backend**: Django 6.0.4
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Payment**: Razorpay API
- **Admin**: Jazzmin (styled Django admin)
- **Authentication**: JWT tokens + OTP verification

## 📋 Requirements

- Python 3.10+
- pip
- Virtual Environment

## 🚀 Installation & Setup

### 1. Clone/Download Project
```bash
cd easymart
```

### 2. Create Virtual Environment
```bash
python -m venv env
# Activate it
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy the template
cp .env.example .env

# Edit .env with your configuration
# Required: EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
# Optional: RAZORPAY keys for payment
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Admin Account
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit:
- **Frontend**: http://127.0.0.1:8000
- **Admin**: http://127.0.0.1:8000/admin

## 📚 API Endpoints

### Authentication
- `POST /accounts/api/login/` - API login
- `POST /accounts/api/send-otp/` - Send OTP to email
- `POST /accounts/api/verify-otp/` - Verify OTP
- `POST /accounts/signup/` - Create account
- `GET /accounts/logout/` - Logout

### Products
- `GET /products/home/` - Product list with filters
- `GET /products/product/<id>/` - Product details
- `GET /products/category/` - Category list

### Cart (Authenticated)
- `GET /cart/` - View cart
- `POST /cart/add/` - Add to cart (AJAX)
- `POST /cart/update/` - Update quantity (AJAX)
- `GET /cart/remove/<id>/` - Remove item
- `POST /cart/remove-ajax/` - Remove via AJAX

### Orders (Authenticated)
- `GET /orders/checkout/` - Checkout page
- `POST /orders/create-razorpay-order/` - Create Razorpay order
- `POST /orders/verify-payment/` - Verify payment
- `POST /orders/place-cod-order/` - Place COD order
- `GET /orders/history/` - Order history
- `GET /orders/detail/<id>/` - Order details
- `GET /orders/track/<id>/` - Track order

## 🔒 Security Features

### Development
- CSRF protection enabled
- XFrame options set to DENY
- Content type nosniff enabled
- Session cookies with HTTPONLY flag

### Production (Configure in .env)
- SSL/HTTPS redirect
- Secure session cookies
- Secure CSRF cookies
- HSTS headers
- Strong SECRET_KEY required

## 📦 Sample Data

The application auto-generates sample products on first load with:
- 24 sample products across 6 categories
- Auto-category creation
- Product descriptions

Products include:
- 🍎 Fruits (Apple, Banana, Mango, Orange)
- 🥬 Vegetables (Carrot, Tomato, Onion, Potato)
- 🥛 Dairy (Milk, Butter, Cheese, Curd)
- 🍞 Bakery (Bread, Cake, Bun, Croissant)
- 🥤 Beverages (Juice, Tea, Coffee, Cold Drink)
- 🍿 Snacks (Chips, Biscuits, Namkeen, Popcorn)

## 🎯 Key Models

### User (Custom)
- Email-based authentication
- Phone number field
- OTP codes management
- Address management

### Product
- Categories with slugs
- Price with discount
- Stock management
- Image upload
- Auto slug generation

### Cart
- Session-based guest cart
- Per-user authenticated cart
- Real-time item tracking

### Order
- Multi-status workflow (Pending → Delivered)
- Payment method tracking
- Razorpay integration
- Order items snapshot

### Address
- Multiple addresses per user
- Default address support
- Full address details

## 🧪 Testing

### Manual Testing Checklist
- [ ] Home page loads with sample products
- [ ] Login/Signup works
- [ ] Add item to cart
- [ ] Update cart quantities
- [ ] Checkout page shows correct total
- [ ] Order history displays
- [ ] Admin panel accessible

### Running Tests
```bash
python manage.py test
```

## 🚀 Production Deployment

### Before Deployment
1. Update .env with production values
2. Set `DEBUG=False`
3. Generate strong `SECRET_KEY` (use https://djecrety.ir/)
4. Configure allowed hosts
5. Set up SSL/HTTPS
6. Use PostgreSQL instead of SQLite

### Database Migration (Production)
```bash
# Backup current database
# Configure PostgreSQL in .env
python manage.py migrate --database production
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Production Server Options
- Gunicorn + Nginx
- uWSGI + Apache
- AWS/Heroku with buildpacks

### Using Gunicorn
```bash
pip install gunicorn
gunicorn easymart.wsgi:application --bind 0.0.0.0:8000
```

## 📝 Configuration Files

### Key Settings
- `easymart/settings.py` - Main Django configuration
- `easymart/urls.py` - URL routing
- `easymart/context_processors.py` - Template context
- `.env` - Environment variables

### App URLs
- `accounts/urls.py` - Authentication routes
- `products/urls.py` - Product routes
- `cart/urls.py` - Cart routes
- `orders/urls.py` - Order routes

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'dotenv'
```bash
pip install python-dotenv
```

### Port 8000 already in use
```bash
python manage.py runserver 8001
```

### Database locked
```bash
# Delete db.sqlite3 and run migrations again
rm db.sqlite3
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic
```

## 📞 Support

For issues or improvements:
1. Check the logs in `logs/django.log`
2. Run `python manage.py check` for diagnostics
3. Review .env configuration
4. Check database migrations

## 📄 License

This project is provided as-is for educational and commercial use.

## 🎉 Status

✅ **Project Complete & Working**
- All core features implemented
- Database configured and migrated
- Authentication system working
- Payment integration ready
- Admin panel configured
- Sample data auto-generated
- Production-ready with configuration

**Ready for Development or Deployment!**
