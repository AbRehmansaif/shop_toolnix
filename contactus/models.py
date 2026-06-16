from django.db import models

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('order', 'Order Tracking & Support'),
        ('partnership', 'Partnership & Product Listing'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='general')
    order_number = models.CharField(max_length=50, blank=True, help_text="Optional: Provide your order number for faster support.")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_subject_display()} from {self.name}"

    class Meta:
        ordering = ['-created_at']
