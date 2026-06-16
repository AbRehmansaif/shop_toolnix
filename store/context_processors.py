from .models import Category

def site_context(request):
    return {
        "site_name": "ShopToolnix",
        "site_tagline": "Best Deals. Trusted Reviews.",
        "categories": Category.objects.filter(parent__isnull=True).prefetch_related('subcategories'),
    }
