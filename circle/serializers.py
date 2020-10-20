from rest_framework import serializers
from .models import Circle, CircleMembership

class CircleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Circle
        fields = ['url', 'name']

# class CircleMembershipSerializer(serializers.HyperlinkedModelSerializer):
#     circle = CircleSerializer()

#     class Meta:
#         model = CircleMembership
#         fields = ['url', 'circle', 'role', 'joined_at']
