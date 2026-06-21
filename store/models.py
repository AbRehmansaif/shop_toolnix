from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default="🛍️")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    show_on_homepage = models.BooleanField(default=False, help_text="Check to display this subcategory directly on the parent's homepage card.")
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=255, blank=True, help_text="SEO Title. Falls back to name.")
    meta_description = models.TextField(blank=True, help_text="SEO Description. Falls back to description.")
    order = models.IntegerField(default=0)

    @property
    def homepage_subcategories(self):
        return self.subcategories.filter(show_on_homepage=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    PLATFORM_CHOICES = [
        ("amazon", "Amazon"),
        ("ebay", "eBay"),
        ("shareasale", "ShareASale"),
        ("clickbank", "ClickBank"),
        ("cj", "CJ Affiliate"),
        ("dropship", "Dropship Direct"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextUploadingField()
    short_description = models.CharField(max_length=300, blank=True)
    meta_title = models.CharField(max_length=255, blank=True, help_text="SEO Title. Falls back to title.")
    meta_description = models.TextField(blank=True, help_text="SEO Description. Falls back to short_description or truncated description.")
    image_url = models.URLField(blank=True)
    affiliate_url = models.URLField(blank=True, null=True)
    is_affiliate = models.BooleanField(default=True, help_text="Enable to show the affiliate buy button.")
    is_out_of_stock = models.BooleanField(default=False, help_text="If checked, the product is displayed but the buy button is disabled.")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="amazon")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percent = models.IntegerField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    review_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_deal_of_day = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    frequently_bought_together = models.ManyToManyField("self", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.original_price and self.sale_price and not self.discount_percent:
            self.discount_percent = int(
                ((self.original_price - self.sale_price) / self.original_price) * 100
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def display_price(self):
        return self.sale_price or self.original_price


class ProductLink(models.Model):
    product = models.ForeignKey(Product, related_name='additional_links', on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=Product.PLATFORM_CHOICES)
    url = models.URLField()
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    button_text = models.CharField(max_length=50, blank=True, help_text="Optional custom text, e.g., 'Buy on Amazon'")

    class Meta:
        ordering = ['platform']

    def __str__(self):
        return f"{self.product.title} - {self.get_platform_display()}"


class ProductHighlight(models.Model):
    product = models.ForeignKey(Product, related_name='highlights', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.title} - Highlight"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.title} - {self.name}"


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    cover_image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    related_products = models.ManyToManyField(Product, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
