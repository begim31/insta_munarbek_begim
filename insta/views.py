from django.db.models import Q
from rest_framework import generics, status, filters
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import Post, FavouritePost, Comment, Follow, Image, Tag, UserProfile
from .serializers import UserRegisterSerializer, LoginSerializer, PostSerializer, FavouritePostSerializer, \
    CommentSerializer, FollowSerializer, UserSerializer, ImageSerializer, TagSerializer, UserProfileSerializer
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = 'detail'
        context['request'] = self.request
        return context

class UserProfileView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    def get_serializer_context(self):
        return {'request': self.request}

class UserRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

class CustomAuthToken(ObtainAuthToken):
    serializer_class = LoginSerializer

class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)

class PostList(generics.ListCreateAPIView):
    search_fields = ['description']
    filter_backends = (filters.SearchFilter,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Post.objects.all()
        q = self.request.query_params.get('q', None)
        if q is not None:
            queryset = queryset.filter(Q(author__username__icontains=q) | Q(tags__title__icontains=q))
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_permissions(self):
        if self.request.method in ['post']:
            permissions = [IsAuthenticated, ]
        elif self.request.method in ['put', 'patch', 'delete']:
            permissions = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permissions = []
        return [permission() for permission in permissions]


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = 'detail'
        return context

class ImageView(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    # permission_classes = [IsAuthenticated]

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class FavouritePostList(generics.ListCreateAPIView):
    serializer_class = FavouritePostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return FavouritePost.objects.filter(user=self.request.user)


class FavouritePostDestroy(generics.DestroyAPIView):
    queryset = FavouritePost.objects.all()
    serializer_class = FavouritePostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)


class CommentsList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, )


class FollowersList(generics.ListCreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
