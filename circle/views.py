from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser, JSONParser
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated
from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from circle.models import Circle, CircleInvitation, CircleRole, Post, User
from circle.serializers import (
    CircleInvitationAcceptSerializer,
    CircleInvitationSerializer,
    CircleSerializer,
    PostInSerializer,
    PostOutSerializer,
)

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


class IsCircleOwner(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        owners = User.objects.filter(
            memberships__circle=obj, memberships__role=CircleRole.OWNER
        )
        return request.user in owners


class IsPostAuthor(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.author


class CircleViewSet(ModelViewSet):
    serializer_class = CircleSerializer
    permission_classes = [IsAuthenticated, IsCircleOwner]
    pagination_class = None

    def get_queryset(self):
        return self.request.user.circles.all()

    def perform_create(self, serializer):
        """
        The current user needs to be added to the circle
        as an owner.
        """
        circle = serializer.save()
        circle.memberships.create(user=self.request.user, role=CircleRole.OWNER)


class PostViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsPostAuthor]
    parser_classes = [JSONParser, FileUploadParser]

    @action(detail=False)
    def mine(self, request):
        posts = Post.objects.filter(author=self.request.user).order_by("-posted_at")
        serializer = PostOutSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["PUT"])
    def image(self, request, pk, format=None):
        if "file" not in request.data:
            raise ParseError("Empty content")

        file = request.data["file"]
        post = self.get_object()

        post.image.save(file.name, file, save=True)
        return Response(status=201)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return PostOutSerializer
        return PostInSerializer

    def get_queryset(self):
        posts = Post.objects.select_related("author", "circle").prefetch_related(
            "circle__members"
        )
        circle_pk = self.request.query_params.get("circle", None)
        if circle_pk:
            posts = posts.filter(circle__pk=circle_pk)

        # Filter the posts to only ones that are in a circle where the current user
        # is a member. We can use an exact match from the relationship to one user.
        return posts.filter(circle__members=self.request.user).order_by("-posted_at")

    def get_parser_classes(self):
        print(self.action)
        if self.action == "image":
            return [FileUploadParser]

        return [JSONParser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CircleInvitationViewSet(ViewSet):
    """
    GET /invitations/ -- get all your invites to circles
    GET /invitations/?circle=circle_pk -- get all invites to a circle (if you are an owner or admin)
    GET /invitations/<pk>/ -- view an invitation to a circle
    POST /invitations/ -- create an invitation to a circle (if you are an owner or admin)
    PATCH /invitations/<pk>/ -- accept an invitation (if you are the invited person)
    DELETE /invitations/<pk>/ -- delete invitation (if you are the invitee or an owner or admin of the circle)
    """

    def does_not_have_access(self, invitation, user):
        return not (
            user == invitation.invitee or invitation.circle.is_owner_or_admin(user)
        )

    def list(self, request):
        """Show all invitations for a user or for a circle."""
        circle_pk = self.request.query_params.get("circle", None)
        if circle_pk:
            circle = get_object_or_404(Circle, pk=circle_pk)
            if not circle.is_owner_or_admin(request.user):
                raise PermissionDenied(
                    detail="You must be an owner or admin of the circle."
                )
            invitations = circle.invitations.all()
        else:
            invitations = request.user.invitations.all()

        serializer = CircleInvitationSerializer(
            instance=invitations,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def create(self, request):
        serializer = CircleInvitationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        circle = serializer.validated_data["circle"]
        invitee = serializer.validated_data["invitee"]
        if not circle.is_owner_or_admin(request.user):
            raise PermissionDenied(
                detail="You must be an owner or admin of the circle to invite someone."
            )
        if invitee in circle.members.all():
            raise ValidationError(detail="This user is already in this circle.")
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        invitation = get_object_or_404(CircleInvitation, pk=pk)

        # DeMorgan's Law
        # not a and not b == not (a or b)

        if self.does_not_have_access(invitation, request.user):
            raise PermissionDenied(
                detail="You must be the invitee or an owner or admin of the circle."
            )
        serializer = CircleInvitationSerializer(
            instance=invitation, context={"request": request}
        )
        return Response(serializer.data)

    def partial_update(self, request, pk):
        invitation = get_object_or_404(CircleInvitation, pk=pk)
        if request.user != invitation.invitee:
            raise PermissionDenied(detail="You must be the invitee.")
        serializer = CircleInvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation.accept()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        invitation = get_object_or_404(CircleInvitation, pk=pk)
        if self.does_not_have_access(invitation, request.user):
            raise PermissionDenied(
                detail="You must be the invitee or an owner or admin of the circle."
            )

        invitation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
