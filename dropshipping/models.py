import random
import string
import secrets
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    logo_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class DropProduct(models.Model):
    """Links a store Product to a dropshipping supplier with cost & logistics info."""
    product = models.OneToOneField(
        'store.Product', on_delete=models.CASCADE, related_name='drop_info'
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products'
    )
    supplier_url = models.URLField(
        help_text="Direct product URL on AliExpress / supplier site"
    )
    supplier_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Cost YOU pay the supplier (in USD)"
    )
    shipping_days_min = models.IntegerField(default=7)
    shipping_days_max = models.IntegerField(default=21)
    stock = models.IntegerField(default=999, help_text="Available stock (approximate)")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Internal notes about this drop product")

    # Shipping and Payment configurations
    shipping_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Shipping cost per unit for this product"
    )
    allow_cod = models.BooleanField(default=True, verbose_name="Allow Cash on Delivery")
    allow_bank = models.BooleanField(default=True, verbose_name="Allow Bank Transfer")
    allow_stripe = models.BooleanField(default=True, verbose_name="Allow Stripe / Card")
    allow_paypal = models.BooleanField(default=True, verbose_name="Allow PayPal")

    def profit_margin(self):
        price = self.product.display_price
        if price and self.supplier_cost:
            return price - self.supplier_cost
        return None

    def profit_percent(self):
        price = self.product.display_price
        if price and self.supplier_cost and price > 0:
            return round(((price - self.supplier_cost) / price) * 100, 1)
        return None

    def __str__(self):
        return f"Drop: {self.product.title}"

    class Meta:
        verbose_name = "Drop Product"
        verbose_name_plural = "Drop Products"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   '⏳ Pending Payment'),
        ('paid',      '💳 Paid'),
        ('ordered',   '📦 Ordered from Supplier'),
        ('shipped',   '🚚 Shipped'),
        ('delivered', '✅ Delivered'),
        ('cancelled', '❌ Cancelled'),
        ('refunded',  '↩️ Refunded'),
    ]

    PAYMENT_CHOICES = [
        ('cod',    'Cash on Delivery'),
        ('bank',   'Bank Transfer'),
        ('stripe', 'Stripe / Card'),
        ('paypal', 'PayPal'),
    ]

    order_number  = models.CharField(max_length=20, unique=True, blank=True)
    # Customer info
    first_name    = models.CharField(max_length=100, default='')
    last_name     = models.CharField(max_length=100, default='')
    email         = models.EmailField()
    phone         = models.CharField(max_length=20)
    
    # Shipping address
    country       = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city          = models.CharField(max_length=100)
    state         = models.CharField(max_length=100)
    postal_code   = models.CharField(max_length=20)
    
    # Delivery Instructions
    delivery_notes       = models.TextField(blank=True)
    leave_at_front_door  = models.BooleanField(default=False)
    call_before_delivery = models.BooleanField(default=False)
    gate_code            = models.CharField(max_length=50, blank=True)
    # Payment & status
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')], default='pending')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # Financials
    subtotal      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes    = models.TextField(blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate a cryptographically secure 12-character hex string (approx 48 bits of entropy)
            # This makes the order number practically unguessable, protecting customer data on tracking page.
            self.order_number = 'ORD-' + secrets.token_hex(6).upper()
        super().save(*args, **kwargs)

    @property
    def is_safe_to_ship(self):
        """Strict security check: Only ship if payment is confirmed or it's Cash on Delivery."""
        return self.payment_status == 'paid' or self.payment_method == 'cod'

    def get_status_color(self):
        colors = {
            'pending':   '#F59E0B',
            'paid':      '#3B82F6',
            'ordered':   '#8B5CF6',
            'shipped':   '#06B6D4',
            'delivered': '#10B981',
            'cancelled': '#EF4444',
            'refunded':  '#6B7280',
        }
        return colors.get(self.status, '#6B7280')

    def __str__(self):
        return f"Order #{self.order_number} — {self.full_name}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product       = models.ForeignKey('store.Product', on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=255)       # snapshot at order time
    product_image = models.URLField(blank=True)            # snapshot
    supplier_url  = models.URLField(blank=True)            # snapshot for admin to order
    supplier_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity      = models.IntegerField(default=1)
    unit_price    = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        if self.unit_price is None or self.quantity is None:
            return 0
        return self.unit_price * self.quantity

    @property
    def profit(self):
        if self.unit_price is None or self.quantity is None:
            return None
        if self.supplier_cost:
            return (self.unit_price - self.supplier_cost) * self.quantity
        return None

    def __str__(self):
        return f"{self.product_title} × {self.quantity}"

    class Meta:
        verbose_name = "Order Item"


class OrderStatusUpdate(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates')
    status     = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    note       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.order.status != self.status:
            self.order.status = self.status
            self.order.save(update_fields=['status', 'updated_at'])

    def __str__(self):
        return f"#{self.order.order_number} → {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Status Update"
