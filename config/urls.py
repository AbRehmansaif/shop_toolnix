from django.contrib import admin
from django.urls import path, include
from config.legacy_auth import legacy_admin_view
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from store.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap
from django.views.generic import TemplateView

admin.site.site_header = "ShopToolnix Administration"
admin.site.site_title = "ShopToolnix Admin Portal"
admin.site.index_title = "Welcome to ShopToolnix Admin"

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', legacy_admin_view, name='legacy_admin'),
    path('store-management-portal/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('blogs/', include('blogs.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('store.urls')),
    path('', include('dropshipping.urls')),
    path('', include('contactus.urls')),
    path('payment/', include('paymentsystem.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
