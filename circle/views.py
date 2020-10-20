from circle.models import CircleRole, User
from rest_framework import serializers
from circle.serializers import CircleSerializer
from rest_framework.views import APIView, Response
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

"""
- viewset for posts
    - what does GET /posts/ give us?
        - by default, show all posts visible to the current user
        - use GET params to see all posts for one circle or all your posts
    - create post - specify circle
    - make sure you own a post to update and delete it
    - make sure you are allowed to see a post for GET /posts/<pk>/

- viewset for circles
    - GET /circles/ - show all circles you're in
    - POST /circles/ - make sure you own the circle
    - for update and delete, make sure you are the owner of the circle

- separate view to add a new circle member
"""


class ExampleView(APIView):
    def get(self, request):
        return Response({"ok": True})

class IsCircleOwner(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        owners = User.objects.filter(
            memberships__circle=obj,
            memberships__role=CircleRole.OWNER)
        return request.user in owners

class CircleViewSet(ModelViewSet):
    serializer_class = CircleSerializer
    permission_classes = [IsAuthenticated, IsCircleOwner]

    def get_queryset(self):
        return self.request.user.circles

    def perform_create(self, serializer):
        """
        The current user needs to be added to the circle
        as an owner.
        """
        circle = serializer.save()
        circle.memberships.create(
            user=self.request.user,
            role=CircleRole.OWNER
        )

