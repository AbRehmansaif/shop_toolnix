from django.views.generic import ListView, DetailView
from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from .models import BlogPost, Category

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blogs/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published').select_related('category', 'author').order_by('-created_at')
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blogs/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = BlogPost.objects.filter(status='published').exclude(id=self.object.id).order_by('-created_at')[:5]
        return context

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at
