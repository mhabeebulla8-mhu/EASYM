from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from products.models import Product

# Helps Pylance understand reverse relation
if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


# =========================================
# 🛒 CART MODEL
# =========================================
class Cart(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Cart #{self.pk} - {self.user}"

    # 👇 PYLANCE TYPE HINT (fixes "items unknown" error)
    if TYPE_CHECKING:
        items: RelatedManager["CartItem"]

    # =====================================
    # TOTAL PRICE
    # =====================================
    def get_total_price(self):
        total = Decimal('0.00')

        for item in self.items.select_related('product').all():
            total += item.get_total_price()

        return total

    # =====================================
    # TOTAL ITEMS
    # =====================================
    def get_total_items(self):
        return (
            self.items.aggregate(
                total=models.Sum('quantity')
            )['total']
            or 0
        )


# =========================================
# 📦 CART ITEM MODEL
# =========================================
class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    # =====================================
    # TOTAL PRICE
    # =====================================
    def get_total_price(self):
        return self.product.discounted_price * self.quantity

    # =====================================
    # IMAGE
    # =====================================
    def get_image(self):
        if self.product.image:
            return self.product.image.url
        return '/static/images/default.png'