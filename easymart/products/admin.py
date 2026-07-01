from django.contrib import admin
from django.utils.html import format_html

from .models import Product, Category, Offer


# ============================
# 🔥 OFFER ADMIN (UPGRADED)
# ============================
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'order', 'image_preview')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'category')
    search_fields = ('title',)
    ordering = ('order',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" style="border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = "Preview"


# ============================
# 🔹 CATEGORY ADMIN
# ============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


# ============================
# 🔹 PRODUCT ADMIN (PRO LEVEL)
# ============================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'price',
        'discount',
        'get_discounted_price_display',
        'weight',
        'stock',
        'available',
        'image_preview'
    )

    list_filter = (
        'category',
        'available',
        'discount',
        'created_at'
    )

    search_fields = (
        'name',
        'description'
    )

    ordering = ('-created_at',)

    list_editable = (
        'price',
        'discount',
        'stock',
        'available'
    )

    list_display_links = ('name',)

    fieldsets = (

        ("📦 Product Info", {
            'fields': ('name', 'category', 'description')
        }),

        ("💰 Pricing & Discount", {
            'fields': ('price', 'discount')
        }),

        ("📸 Image", {
            'fields': ('image',)
        }),

        ("📊 Inventory", {
            'fields': ('stock', 'available')
        }),

        ("⏱ Metadata", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),

    )
    
    def get_discounted_price_display(self, obj):
        if obj.discount > 0:
            return f"₹{obj.discounted_price:.2f}"
        return "—"
    
    get_discounted_price_display.short_description = "Discounted Price"

    readonly_fields = ('created_at', 'updated_at')

    # ✅ IMAGE PREVIEW
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:6px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = "Preview"