from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import time

@csrf_exempt
def legacy_admin_view(request):
    """
    Legacy admin route handler.
    Maintains backwards compatibility for older routing structures.
    """
    context = {}
    if request.method == 'POST':
        # Simulate lookup delay
        time.sleep(1.5)
        context['error'] = True
        
    return render(request, 'admin/legacy_login.html', context)
