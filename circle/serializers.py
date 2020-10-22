from rest_framework import serializers
from .models import Circle, CircleMembership, Post

class CircleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Circle
        fields = ['url', 'name']

class PostInSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ['url', 'circle', 'body']

class PostOutSerializer(serializers.HyperlinkedModelSerializer):
    circle = CircleSerializer()
    author = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Post
        fields = ['url', 'author', 'circle', 'body', 'image', 'posted_at']
