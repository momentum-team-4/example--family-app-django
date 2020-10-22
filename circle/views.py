from circle.models import CircleRole, Post, User
from rest_framework.decorators import action
from circle.serializers import CircleSerializer, PostInSerializer, PostOutSerializer
from rest_framework.views import APIView, Response
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.exceptions import ParseError


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

class PostViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsPostAuthor]
    parser_classes = [JSONParser, FileUploadParser]

    @action(detail=False)
    def mine(self, request):
        posts = Post.objects.filter(author=self.request.user).order_by("-posted_at")
        serializer = PostOutSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['PUT'])
    def image(self, request, pk, format=None):
        if 'file' not in request.data:
            raise ParseError('Empty content')

        file = request.data['file']
        post = self.get_object()

        post.image.save(file.name, file, save=True)
        return Response(status=201)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return PostOutSerializer
        return PostInSerializer

    def get_queryset(self):
        posts = Post.objects
        circle_pk = self.request.query_params.get('circle', None)
        if circle_pk:
            posts = posts.filter(circle__pk=circle_pk)

        # Filter the posts to only ones that are in a circle where the current user
        # is a member. We can use an exact match from the relationship to one user.
        return posts.filter(circle__members=self.request.user).order_by("-posted_at")

    def get_parser_classes(self):
        print(self.action)
        if self.action == 'image':
            return [FileUploadParser]

        return [JSONParser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
