from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# ======================================================
# CATEGORY MODEL
# ======================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ======================================================
# PRODUCT MODEL
# ======================================================

class Product(models.Model):

    # CATEGORY
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    # BASIC INFO
    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    # PRICE
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    discount = models.PositiveIntegerField(
        default=0,
        help_text="Discount percentage (0-100)"
    )

    # IMAGE
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    # EXTRA INFO
    weight = models.CharField(
        max_length=20,
        default="500g"
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    available = models.BooleanField(
        default=True
    )

    # TIMESTAMPS
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ['-updated_at', '-created_at']

        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['available']),
            models.Index(fields=['category', 'available']),
            models.Index(fields=['-updated_at']),
        ]

    # ==================================================
    # VALIDATION
    # ==================================================

    def clean(self):

        if self.discount < 0 or self.discount > 100:
            raise ValidationError(
                "Discount must be between 0 and 100"
            )

        if self.price < 0:
            raise ValidationError(
                "Price cannot be negative"
            )

        if self.stock < 0:
            raise ValidationError(
                "Stock cannot be negative"
            )

    # ==================================================
    # SAVE
    # ==================================================

    def save(self, *args, **kwargs):

        # VALIDATE FIRST
        self.full_clean()

        # AUTO SLUG
        if not self.slug:

            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            while Product.objects.filter(
                slug=unique_slug
            ).exclude(pk=self.pk).exists():

                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        # AUTO STOCK AVAILABILITY
        self.available = self.stock > 0

        super().save(*args, **kwargs)

    # ==================================================
    # STRING
    # ==================================================

    def __str__(self):
        return self.name

    # ==================================================
    # IMAGE URL
    # ==================================================

    @property
    def image_url(self):

        if self.image:
            return self.image.url

        return "/static/images/default.png"

    # ==================================================
    # DISCOUNT AMOUNT
    # ==================================================

    @property
    def discount_amount(self):

        if self.discount > 0:

            return (
                self.price *
                Decimal(self.discount / 100)
            ).quantize(Decimal('0.01'))

        return Decimal('0.00')

    # ==================================================
    # FINAL DISCOUNTED PRICE
    # ==================================================

    @property
    def discounted_price(self):

        if self.discount > 0:

            final_price = self.price - self.discount_amount

            if final_price < 0:
                return Decimal('0.00')

            return final_price.quantize(
                Decimal('0.01')
            )

        return self.price.quantize(
            Decimal('0.01')
        )

    # ==================================================
    # PERCENT SAVED TEXT
    # ==================================================

    @property
    def savings_text(self):

        if self.discount > 0:
            return f"{self.discount}% OFF"

        return ""


# ======================================================
# OFFER / HERO BANNER MODEL
# ======================================================

class Offer(models.Model):

    title = models.CharField(
        max_length=100
    )

    subtitle = models.CharField(
        max_length=150,
        blank=True
    )

    image = models.ImageField(
        upload_to='offers/'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='offers'
    )

    start_date = models.DateTimeField(
        null=True,
        blank=True
    )

    end_date = models.DateTimeField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['order', '-updated_at']

    # ==================================================
    # VALID OFFER CHECK
    # ==================================================

    @property
    def is_valid(self):

        now = timezone.now()

        if not self.is_active:
            return False

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True

    def __str__(self):
        return self.title