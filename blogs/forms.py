from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-surface/50 border border-outline-variant/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary transition-colors', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-surface/50 border border-outline-variant/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary transition-colors', 'placeholder': 'Your Email'}),
            'body': forms.Textarea(attrs={'class': 'w-full bg-surface/50 border border-outline-variant/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary transition-colors', 'placeholder': 'Your Comment', 'rows': 4}),
        }
