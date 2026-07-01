# EasyMart Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Prerequisites
- Python 3.10+ installed
- Virtual environment ready

### Step 2: Install Dependencies
```bash
# Activate virtual environment
env\Scripts\activate  # Windows
source env/bin/activate  # Mac/Linux

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Create .env file
copy .env.example .env

# Edit .env with your values (minimum required):
# - EMAIL_HOST_USER=your-email@gmail.com
# - EMAIL_HOST_PASSWORD=your-app-password
```

### Step 4: Setup Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Step 5: Run Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## 🔐 Admin Access

1. Go to: http://127.0.0.1:8000/admin
2. Login with superuser credentials created above
3. Manage products, orders, users, categories

---

## 🛒 Key Workflows

### User Registration
1. Click "Create Account" on homepage
2. Enter email and password (min 6 chars)
3. System sends OTP to email
4. Verify OTP to complete signup

### Shopping
1. Browse products on homepage
2. Filter by category
3. Search for products
4. Click "Add to Cart" on any product
5. View cart at `/cart/`

### Checkout
1. Login to your account
2. Add items to cart
3. Go to checkout
4. Select payment method (Online/COD)
5. Complete payment or confirm COD

### Track Orders
1. Login to account
2. View "Order History"
3. See real-time status updates
4. Track delivery status

---

## 📊 Sample Data

The app auto-creates 24 sample products across 6 categories:
- Fruits, Vegetables, Dairy, Bakery, Beverages, Snacks

**First Load**: Sample products are created automatically.

---

## 🧹 Useful Commands

### Database
```bash
# Check migrations
python manage.py showmigrations

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Delete everything and start fresh
python manage.py flush
```

### Testing
```bash
# Run Django checks
python manage.py check

# Run deployment checks
python manage.py check --deploy

# Run tests
python manage.py test
```

### Static/Media
```bash
# Collect static files
python manage.py collectstatic

# Clean static files
python manage.py collectstatic --clear
```

---

## 🚀 Production Checklist

Before deploying, ensure:

- [ ] `.env` file configured with production values
- [ ] `DEBUG = False` in .env
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` set to your domain
- [ ] Email credentials configured
- [ ] RAZORPAY keys added (if using payments)
- [ ] Database migrated
- [ ] Static files collected
- [ ] HTTPS/SSL enabled
- [ ] Using PostgreSQL (not SQLite)

### Production .env Template
```
DEBUG=False
SECRET_KEY=your-long-random-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 🆘 Troubleshooting

### Q: ModuleNotFoundError: No module named 'dotenv'
**A**: Run `pip install python-dotenv`

### Q: Port 8000 already in use
**A**: Run `python manage.py runserver 8001`

### Q: Database locked
**A**: Delete `db.sqlite3` and run `python manage.py migrate`

### Q: Emails not sending
**A**: Check .env EMAIL settings and Gmail App Password

### Q: Static files not showing
**A**: Run `python manage.py collectstatic`

### Q: Admin panel looks broken
**A**: Ensure Jazzmin is installed: `pip install django-jazzmin`

---

## 📞 Important Files

- `easymart/settings.py` - Main configuration
- `.env` - Environment variables (create from .env.example)
- `requirements.txt` - Python dependencies
- `manage.py` - Django management commands
- `db.sqlite3` - Database (auto-created)

---

## 🎯 Features Ready to Use

✅ User authentication with OTP
✅ Product catalog with search & filter
✅ Shopping cart (session-based for guests)
✅ Order management
✅ Payment integration (Razorpay)
✅ Order tracking
✅ Admin dashboard
✅ Email notifications
✅ Multiple addresses
✅ Discounts & offers

---

**Project is ready to run. Start with Step 1 above!**
