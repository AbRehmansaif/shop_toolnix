from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("go/<slug:slug>/", views.track_click, name="track_click"),
    path("deals/", views.deals, name="deals"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("guides/", views.subcategory_pages_list, name="guides_list"),
    path("search/", views.search, name="search"),
    path("best-smart-home-security-system/", views.best_smart_home_security_system_2026, name="best_smart_home_security_system_2026"),
]
