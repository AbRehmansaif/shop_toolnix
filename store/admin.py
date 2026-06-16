from django.contrib import admin
from .models import Category, Tag, Product, BlogPost, ProductLink, ProductHighlight, ProductSpecification


class ProductLinkInline(admin.TabularInline):
    model = ProductLink
    extra = 1

class ProductHighlightInline(admin.TabularInline):
    model = ProductHighlight
    extra = 3

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "show_on_homepage", "icon", "order"]
    list_filter = ["parent", "show_on_homepage"]
    list_editable = ["show_on_homepage", "order"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "platform", "display_price", "is_featured", "is_deal_of_day", "click_count", "is_active", "is_out_of_stock"]
    list_filter = ["platform", "category", "is_featured", "is_deal_of_day", "is_active", "is_out_of_stock", "is_affiliate"]
    list_editable = ["is_featured", "is_deal_of_day", "is_active", "is_out_of_stock"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "description", "brand"]
    filter_horizontal = ["tags", "frequently_bought_together"]
    inlines = [ProductLinkInline, ProductHighlightInline, ProductSpecificationInline]
    fieldsets = (
        ("Basic Info", {"fields": ("title", "brand", "slug", "short_description", "description", "image_url")}),
        ("Affiliate", {"fields": ("is_affiliate", "affiliate_url", "platform")}),
        ("Pricing", {"fields": ("original_price", "sale_price", "discount_percent")}),
        ("Classification", {"fields": ("category", "tags", "frequently_bought_together", "rating", "review_count")}),
        ("Visibility", {"fields": ("is_featured", "is_deal_of_day", "is_active", "is_out_of_stock")}),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_published", "created_at"]
    list_editable = ["is_published"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["tags", "related_products"]
