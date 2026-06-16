from django import forms
from django.core.exceptions import ValidationError
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    # Honeypot field for bot protection (hidden in frontend)
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'style': 'display:none;', 'autocomplete': 'off'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'order_number', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Full Name', 'maxlength': '150'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com', 'maxlength': '254'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'order_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional: e.g. ORD-123456', 'maxlength': '50'}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'How can we help you?', 'maxlength': '2000'}),
        }

    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website:
            raise ValidationError("Bot detected.")
        return website
