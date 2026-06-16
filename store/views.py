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
    categories = Category.objects.all()
    return render(request, "store/product_detail.html", {
        "product": product,
        "related": related,
        "categories": categories,
    })


def track_click(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.click_count += 1
    product.save(update_fields=["click_count"])
    if product.affiliate_url:
        return redirect(product.affiliate_url)
    return redirect('product_detail', slug=product.slug)


def deals(request):
    deals = Product.objects.filter(
        is_active=True, discount_percent__isnull=False
    ).order_by("-discount_percent")
    return render(request, "store/deals.html", {"deals": deals})


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
