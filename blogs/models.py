from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    
    featured_image = models.ImageField(upload_to='blog_images/')
    alt_text = models.CharField(max_length=200, blank=True, help_text="Crucial for SEO. Describe the image for search engines.")
    image_caption = models.CharField(max_length=250, blank=True, help_text="Caption displayed below the image.")
    reading_time = models.PositiveIntegerField(default=5, help_text="Reading time in minutes.")
    content = RichTextUploadingField(help_text="Rich text content.")
    excerpt = models.TextField(max_length=500, help_text="Brief summary for the blog list page.")
    
    # SEO Fields
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO title (max 70 chars)")
    meta_description = models.TextField(max_length=160, blank=True, help_text="SEO description (max 160 chars)")
    target_keywords = models.CharField(max_length=250, blank=True, help_text="Comma-separated keywords (e.g. SEO, AI, Growth)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Force generate slug from title to ensure it contains the complete H1
        original_slug = slugify(self.title, allow_unicode=True)
        unique_slug = original_slug
        num = 1
        # Handle duplicate slugs by appending a number
        while BlogPost.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
            unique_slug = f'{original_slug}-{num}'
            num += 1
        
        self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blogs:blog_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

