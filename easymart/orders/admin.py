from django.contrib import admin
from .models import Order, OrderItem


# ============================
# 📦 ORDER ITEM INLINE
# ============================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


# ============================
# 🧾 ORDER ADMIN
# ============================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'total_price',
        'status',
        'created_at'
    )

    list_filter = ('status', 'created_at')

    search_fields = ('user__username', 'id')

    inlines = [OrderItemInline]

    # ✅ STATUS DROPDOWN EDITABLE
    list_editable = ('status',)

    ordering = ('-created_at',)

    # ✅ BULK ACTION
    actions = ['mark_as_confirmed', 'mark_as_delivered']

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Mark selected as Confirmed"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected as Delivered"


# ============================
# 📦 ORDER ITEM ADMIN
# ============================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')