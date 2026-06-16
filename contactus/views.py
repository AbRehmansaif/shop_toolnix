import time
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact_view(request):
    if request.method == 'POST':
        # Rate Limiting: Max 2 submissions per 5 minutes per session
        last_submission = request.session.get('last_contact_submission', 0)
        current_time = time.time()
        
        if current_time - last_submission < 300: # 300s = 5 mins
            submission_count = request.session.get('contact_submission_count', 0)
            if submission_count >= 2:
                messages.error(request, "You are submitting too many requests. Please try again later.")
                return redirect('contact')
            request.session['contact_submission_count'] = submission_count + 1
        else:
            request.session['contact_submission_count'] = 1
            request.session['last_contact_submission'] = current_time

        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully. We will get back to you shortly.")
            return redirect('contact')
        else:
            if 'website' in form.errors:
                # Silently drop bot submissions
                messages.success(request, "Your message has been sent successfully. We will get back to you shortly.")
                return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contactus/contact.html', {'form': form})
def privacy_policy_view(request):
    return render(request, 'contactus/privacy_policy.html')

def terms_of_use_view(request):
    return render(request, 'contactus/terms_of_use.html')

def refund_policy_view(request):
    return render(request, 'contactus/refund_policy.html')
