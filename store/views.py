from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Tag, BlogPost
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def home(request):
    featured_qs = Product.objects.filter(is_featured=True, is_active=True)
    paginator = Paginator(featured_qs, 8)
    page_number = request.GET.get('page')
    featured = paginator.get_page(page_number)
    deal_of_day = Product.objects.filter(is_deal_of_day=True, is_active=True).first()
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    recent_blogs = BlogPost.objects.filter(is_published=True)[:3]
    trending_qs = Product.objects.filter(is_active=True).order_by("-click_count")
    trending_paginator = Paginator(trending_qs, 20)
    trending_page_number = request.GET.get('trending_page')
    trending = trending_paginator.get_page(trending_page_number)
    total_products = Product.objects.filter(is_active=True).count()
    return render(request, "store/home.html", {
        "featured": featured,
        "deal_of_day": deal_of_day,
        "categories": categories,
        "recent_blogs": recent_blogs,
        "trending": trending,
        "total_products": total_products,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    category_slug = request.GET.get("category")
    platform = request.GET.get("platform")
    query = request.GET.get("q")
    sort = request.GET.get("sort", "-created_at")

    if category_slug:
        try:
            selected_cat = Category.objects.get(slug=category_slug)
            if selected_cat.parent is None:
                # It's a parent category — show its own products + all subcategory products
                sub_slugs = list(selected_cat.subcategories.values_list('slug', flat=True))
                all_slugs = [category_slug] + sub_slugs
                products = products.filter(category__slug__in=all_slugs)
            else:
                # It's a subcategory — show only its own products
                products = products.filter(category__slug=category_slug)
        except Category.DoesNotExist:
            products = products.none()

    if platform:
        products = products.filter(platform=platform)
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    sort_map = {
        "newest": "-created_at",
        "price_low": "sale_price",
        "price_high": "-sale_price",
        "popular": "-click_count",
        "rating": "-rating",
    }
    products = products.order_by(sort_map.get(sort, "-created_at"))

    paginator = Paginator(products, 24)
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "store/product_list.html", {
        "products": page_obj,
        "categories": categories,
        "current_category": category_slug,
        "current_platform": platform,
        "query": query,
        "sort": sort,
        "paginator": paginator,
        "page_obj": page_obj,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:20]
    if not related:
        related = Product.objects.filter(is_active=True).exclude(id=product.id)[:20]
    categories = Category.objects.filter(parent__isnull=True)
    deals = Product.objects.filter(is_active=True, is_deal_of_day=True).exclude(id=product.id).order_by("-discount_percent")[:10]
    return render(request, "store/product_detail.html", {
        "product": product,
        "related": related,
        "categories": categories,
        "deals": deals,
    })


def track_click(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.click_count += 1
    product.save(update_fields=["click_count"])
    if product.affiliate_url:
        return redirect(product.affiliate_url)
    return redirect('product_detail', slug=product.slug)


def deals(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    deals_qs = Product.objects.filter(
        is_active=True, is_deal_of_day=True
    ).order_by("-discount_percent")
    
    paginator = Paginator(deals_qs, 24)
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "store/deals.html", {"deals": page_obj, "page_obj": page_obj, "paginator": paginator})


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, "store/blog_list.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "store/blog_detail.html", {"post": post})


def search(request):
    query = request.GET.get("q", "")
    products = Product.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        is_active=True
    ) if query else Product.objects.none()
    return render(request, "store/search.html", {"products": products, "query": query})


def best_smart_home_security_system_2026(request):
    # Fetch products from the home-security-cameras-smart-doorbells category or similar
    # Assuming slug is 'home-security-cameras-smart-doorbells' or we can query by name
    products = Product.objects.filter(
        category__slug__icontains='security',
        is_active=True
    )
    if not products.exists():
        products = Product.objects.filter(
            Q(title__icontains='security') | Q(title__icontains='camera') | Q(title__icontains='doorbell'),
            is_active=True
        )
    if not products.exists():
        # Fallback to display some products if none match the filters
        products = Product.objects.filter(is_active=True)
    
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    current_category = "home-security-cameras-smart-doorbells"
    
    try:
        active_cat = Category.objects.get(slug=current_category)
        if active_cat.parent:
            related_subcats = active_cat.parent.subcategories.all()
            parent_cat = active_cat.parent
        else:
            related_subcats = active_cat.subcategories.all()
            parent_cat = active_cat
    except Category.DoesNotExist:
        # Fallback if slug doesn't exist in db
        parent_cat = Category.objects.filter(parent__isnull=True).first()
        if parent_cat:
            related_subcats = parent_cat.subcategories.all()
            if not related_subcats.exists():
                related_subcats = Category.objects.filter(parent__isnull=True)
        else:
            related_subcats = Category.objects.all()
    
    sort = request.GET.get("sort", "-created_at")
    sort_map = {
        "newest": "-created_at",
        "price_low": "sale_price",
        "price_high": "-sale_price",
        "popular": "-click_count",
        "rating": "-rating",
    }
    products = products.order_by(sort_map.get(sort, "-created_at"))

    return render(request, "subcategory_pages/best_smart_home_security_system_2026.html", {
        "products": products[:20],  # show top 20
        "categories": categories,
        "current_category": current_category,
        "related_subcats": related_subcats,
        "parent_cat": parent_cat,
        "sort": sort,
    })


def subcategory_pages_list(request):
    # Hardcoded list of subcategory/guide pages for now
    guides_data = [
        {
            'title': 'Best Smart Home Security System 2026, Compare & Buy',
            'slug': 'best-smart-home-security-system',
            'excerpt': 'Discover the best smart home security systems 2026, trusted expert reviews, all budgets covered. Compare features side by side and shop smarter today.',
            'category': 'Smart Home > Home Security Cameras, Smart Doorbell Products',
            'created_at': 'June 21, 2026',
            'image_url': '/static/subcategory_pages/images/smart-home-security-devices.jpg',
            'alt_text': 'Collection of smart home security devices including a camera, sensors, and a smart bulb',
            'url_name': 'best_smart_home_security_system_2026'
        }
    ]
    
    paginator = Paginator(guides_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "subcategory_pages/subcategory_pages_list.html", {"page_obj": page_obj})


