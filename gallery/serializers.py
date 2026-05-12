from rest_framework import serializers

from .models import Category, Gallery


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class GallerySerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Nested serializer to include category details

    class Meta:
        model = Gallery
        fields = ['id', 'image', 'title', 'description', 'created_at', 'category']
