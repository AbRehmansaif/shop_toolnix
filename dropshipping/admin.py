from django.contrib import admin
from django.utils.html import format_html
from .models import Supplier, DropProduct, Order, OrderItem, OrderStatusUpdate


# ---------------------------------------------------------------------------
# Supplier Admin
# ---------------------------------------------------------------------------
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'contact_email', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_email')
    list_editable = ('is_active',)


# ---------------------------------------------------------------------------
# Drop Product Admin
# ---------------------------------------------------------------------------
@admin.register(DropProduct)
class DropProductAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'supplier', 'supplier_cost', 'selling_price_col',
        'profit_col', 'shipping_fee', 'stock', 'shipping_range', 'is_active'
    )
    list_filter = ('is_active', 'supplier')
    search_fields = ('product__title', 'supplier__name')
    list_editable = ('is_active', 'stock', 'shipping_fee')
    raw_id_fields = ('product',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('product', 'supplier', 'supplier_url', 'is_active', 'notes')
        }),
        ('Pricing & Logistics', {
            'fields': ('supplier_cost', 'stock', 'shipping_days_min', 'shipping_days_max')
        }),
        ('Shipping & Payments', {
            'fields': ('shipping_fee', 'allow_cod', 'allow_bank', 'allow_stripe', 'allow_paypal')
        }),
    )

    def selling_price_col(self, obj):
        price = obj.product.display_price
        return f'${price}' if price else '—'
    selling_price_col.short_description = 'Sell Price'

    def profit_col(self, obj):
        p = obj.profit_margin()
        pct = obj.profit_percent()
        if p is not None:
            color = '#10B981' if p > 0 else '#EF4444'
            return format_html(
                '<span style="color:{}; font-weight:600;">${} ({}%)</span>',
                color, p, pct
            )
        return '—'
    profit_col.short_description = 'Profit'

    def shipping_range(self, obj):
        return f'{obj.shipping_days_min}–{obj.shipping_days_max} days'
    shipping_range.short_description = 'Shipping'


# ---------------------------------------------------------------------------
# Order Item Inline
# ---------------------------------------------------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_title', 'unit_price', 'quantity', 'subtotal_col', 'profit_col', 'open_supplier_link')
    fields = ('product_title', 'unit_price', 'quantity', 'subtotal_col', 'profit_col', 'open_supplier_link')
    can_delete = False

    def subtotal_col(self, obj):
        return f'${obj.subtotal:.2f}'
    subtotal_col.short_description = 'Subtotal'

    def profit_col(self, obj):
        p = obj.profit
        if p is not None:
            color = '#10B981' if p > 0 else '#EF4444'
            return format_html('<span style="color:{}; font-weight:600;">${:.2f}</span>', color, p)
        return '—'
    profit_col.short_description = 'Profit'

    def open_supplier_link(self, obj):
        if obj.supplier_url:
            return format_html(
                '<a href="{}" target="_blank" style="background:#8B5CF6;color:#fff;padding:4px 10px;border-radius:4px;text-decoration:none;font-size:12px;">📦 Order from Supplier</a>',
                obj.supplier_url
            )
        return '—'
    open_supplier_link.short_description = 'Supplier Action'


# ---------------------------------------------------------------------------
# Status Update Inline
# ---------------------------------------------------------------------------
class StatusUpdateInline(admin.TabularInline):
    model = OrderStatusUpdate
    extra = 1
    fields = ('status', 'note', 'created_at')
    readonly_fields = ('created_at',)


# ---------------------------------------------------------------------------
# Order Admin
# ---------------------------------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'first_name', 'last_name', 'email', 'status_badge',
        'payment_method', 'total_price_col', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'country', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'subtotal', 'total_price')
    list_editable = ('status',) if False else ()   # changed via inline instead
    inlines = [OrderItemInline, StatusUpdateInline]
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📋 Order Info', {
            'fields': ('order_number', 'status', 'payment_method', 'created_at', 'updated_at')
        }),
        ('👤 Customer', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('📍 Shipping Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code')
        }),
        ('🚚 Delivery Instructions', {
            'fields': ('delivery_notes', 'leave_at_front_door', 'call_before_delivery', 'gate_code'),
            'classes': ('collapse',),
        }),
        ('💰 Financials', {
            'fields': ('subtotal', 'shipping_fee', 'total_price')
        }),
        ('📝 Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;">{}</span>',
            obj.get_status_color(), obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_price_col(self, obj):
        return format_html('<strong>${}</strong>', obj.total_price)
    total_price_col.short_description = 'Total'
