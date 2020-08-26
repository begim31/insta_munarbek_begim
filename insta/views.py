from rest_framework import generics, status, filters
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import Post, FavoritesPosts, Comments, Followers
from .serializers import UserRegisterSerializer, LoginSerializer, PostSerializer, FavoritesPostsSerializer, \
    CommentsSerializer, FollowersSerializer
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly



class UserRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


class CustomAuthToken(ObtainAuthToken):
    serializer_class = LoginSerializer


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
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
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)


class FavoritesPostsList(generics.ListCreateAPIView):
    serializer_class = FavoritesPostsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return FavoritesPosts.objects.filter(user=self.request.user)


class FavoritesPostsDestroy(generics.DestroyAPIView):
    queryset = FavoritesPosts.objects.all()
    serializer_class = FavoritesPostsSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)


class CommentsList(generics.ListCreateAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer


class FollowersList(generics.ListCreateAPIView):
    queryset = Followers.objects.all()
    serializer_class = FollowersSerializer

