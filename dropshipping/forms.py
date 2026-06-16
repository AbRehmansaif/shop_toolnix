from django import forms


import re
from django import forms
from django.core.exceptions import ValidationError

class CheckoutForm(forms.Form):
    # Customer info
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=20)
    
    # Shipping address
    country = forms.CharField(max_length=100)
    address_line1 = forms.CharField(max_length=255)
    address_line2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    
    # Delivery Instructions
    delivery_notes = forms.CharField(required=False, widget=forms.Textarea)
    leave_at_front_door = forms.BooleanField(required=False)
    call_before_delivery = forms.BooleanField(required=False)
    gate_code = forms.CharField(max_length=50, required=False)
    
    # Payment Method
    payment_method = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[], # Dynamically populated
    )
    
    def __init__(self, *args, **kwargs):
        available_payment_methods = kwargs.pop('available_payment_methods', [])
        super().__init__(*args, **kwargs)
        
        # Build choices
        choices = []
        if 'cod' in available_payment_methods:
            choices.append(('cod', '💵 Cash on Delivery'))
        if 'bank' in available_payment_methods:
            choices.append(('bank', '🏦 Bank Transfer'))
        if 'stripe' in available_payment_methods:
            choices.append(('stripe', '💳 Stripe / Card'))
        if 'paypal' in available_payment_methods:
            choices.append(('paypal', '🅿️ PayPal'))
            
        self.fields['payment_method'].choices = choices
        if choices:
            self.fields['payment_method'].initial = choices[0][0]

    # Backend security validations
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not re.match(r'^\+?[\d\s\-()]{7,20}$', phone):
            raise ValidationError("Invalid phone number format.")
        return phone

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '')
        if not re.match(r'^[\w\s\-\']+$', name):
            raise ValidationError("Invalid characters in first name.")
        return name

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '')
        if not re.match(r'^[\w\s\-\']+$', name):
            raise ValidationError("Invalid characters in last name.")
        return name

    def clean_country(self):
        country = self.cleaned_data.get('country', '')
        if not re.match(r'^[\w\s\-\']+$', country):
            raise ValidationError("Invalid characters in country.")
        return country

    def clean_city(self):
        city = self.cleaned_data.get('city', '')
        if not re.match(r'^[\w\s\-\']+$', city):
            raise ValidationError("Invalid characters in city.")
        return city

    def clean_state(self):
        state = self.cleaned_data.get('state', '')
        if not re.match(r'^[\w\s\-\']+$', state):
            raise ValidationError("Invalid characters in state.")
        return state

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code', '')
        if not re.match(r'^[\w\s\-]+$', postal_code):
            raise ValidationError("Invalid characters in postal code.")
        return postal_code

    def clean_address_line1(self):
        addr = self.cleaned_data.get('address_line1', '')
        if re.search(r'[<>{}]', addr):
            raise ValidationError("Address contains invalid characters (<, >, {, }).")
        return addr

    def clean_address_line2(self):
        addr = self.cleaned_data.get('address_line2', '')
        if addr and re.search(r'[<>{}]', addr):
            raise ValidationError("Address contains invalid characters (<, >, {, }).")
        return addr

    def clean_delivery_notes(self):
        from django.utils.html import strip_tags
        notes = self.cleaned_data.get('delivery_notes', '')
        # Strip all HTML tags entirely for maximum security
        clean_notes = strip_tags(notes)
        if clean_notes != notes:
             raise ValidationError("HTML tags are not allowed in delivery notes.")
        return clean_notes

    def clean_gate_code(self):
        code = self.cleaned_data.get('gate_code', '')
        if code and not re.match(r'^[\w\s#*]+$', code):
            raise ValidationError("Invalid characters in gate code.")
        return code
