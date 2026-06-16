from django.http import HttpResponseForbidden
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class AdminSecurityMiddleware:
    """
    Bank-level security middleware for the admin login panel.
    Implements advanced bot detection and strict IP-based rate limiting.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 0. Legacy URL Check
        # Scanners blindly go to /admin/
        if request.path.startswith('/admin/') and request.method == 'POST':
            client_ip = self.get_client_ip(request)
            cache_key = f'legacy_auth_{client_ip}'
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 3:
                logger.warning(f"[SECURITY] Banned IP for legacy brute force: {client_ip}")
                return HttpResponseForbidden("Forbidden: Automated attack detected and IP logged.")
                
            # Increment attempts (expires in 600 seconds / 10 mins)
            cache.set(cache_key, attempts + 1, timeout=600)
            # We let it pass through to the view so they experience the fake delay and fake error page

        # 1. Protect the real admin login endpoint
        if request.path.startswith('/store-management-portal/login/') and request.method == 'POST':
            
            # 1. Advanced Bot Check
            # If the hidden 'website_url' field is filled out, it's a bot.
            bot_value = request.POST.get('website_url', '')
            if bot_value:
                logger.warning(f"[SECURITY] Bot detected via invisible field from IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("Forbidden: Automated request detected.")

            # 2. Strict Rate Limiting
            # 3 attempts per 5 minutes per IP
            client_ip = self.get_client_ip(request)
            cache_key = f'admin_login_attempts_{client_ip}'
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 3:
                logger.warning(f"[SECURITY] Rate limit exceeded for IP: {client_ip}")
                return HttpResponseForbidden("Forbidden: Too many login attempts. Please try again later.")
                
            # Increment attempts (expires in 300 seconds / 5 mins)
            cache.set(cache_key, attempts + 1, timeout=300)

        response = self.get_response(request)
        
        # If login was successful, clear the rate limit
        if request.path.startswith('/store-management-portal/login/') and request.method == 'POST':
            # A successful login redirects (status 302) to the admin index
            if response.status_code == 302 and response.url.startswith('/store-management-portal/'):
                client_ip = self.get_client_ip(request)
                cache.delete(f'admin_login_attempts_{client_ip}')

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
