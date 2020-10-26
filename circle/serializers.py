from rest_framework import serializers

from .models import Circle, CircleMembership, CircleInvitation, Post, User


class CircleSerializer(serializers.HyperlinkedModelSerializer):
    members = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = Circle
        fields = ['url', 'name', 'members']

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

class CircleMembershipInvitationSerializer(serializers.HyperlinkedModelSerializer):
    invitee = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = CircleInvitation
        fields = ['url', 'invitee', 'circle', 'role']
