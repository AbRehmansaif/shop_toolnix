from rest_framework import serializers
from .models import BlogPost, Category, Comment
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class AuthorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name']
        
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'name', 'body', 'created_at']

class BlogPostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'category', 'author', 'featured_image_url', 'alt_text', 'reading_time', 'excerpt', 'created_at']

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None

class BlogPostDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'author', 'featured_image_url', 'alt_text', 'image_caption',
            'reading_time', 'content', 'excerpt', 'meta_title', 'meta_description', 'target_keywords',
            'created_at', 'updated_at', 'comments'
        ]

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None

    def get_comments(self, obj):
        comments = obj.comments.filter(active=True)
        return CommentSerializer(comments, many=True).data
