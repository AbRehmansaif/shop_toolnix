from django.urls import path
from django.contrib.sitemaps.views import sitemap
from .views import BlogListView, BlogDetailView, BlogSitemap

app_name = 'blogs'

sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='blog_sitemap'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
]
