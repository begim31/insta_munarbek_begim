from django.urls import path
from .views import (FavouritePostList, FavouritePostDestroy, CommentsList, FollowersList,
                    UserListView, ImageView, TagListCreateView, UserProfileView, UserDetailView)
from insta.views import UserRegister, CustomAuthToken, Logout, PostList, PostDetail, FavouritePostList

urlpatterns = [
    path('users/', UserListView.as_view(), name='users'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    # path('userprofiles/', UserProfileView.as_view(), name='userprofiles'),

    path('register/', UserRegister.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('follow/', FollowersList.as_view(), name='followers'),

    path('posts/', PostList.as_view(), name='post_list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post_detail'),
    # path('images/', ImageView.as_view(), name='images'),
    # path('tags/', TagListCreateView.as_view(), name='tags1,'),

    path('comment/', CommentsList.as_view(), name='comments'),

    path('like/', FavouritePostList.as_view(), name='favourites_list'),
    path('dislike/<pk>/', FavouritePostDestroy.as_view(), name='favourites_destroy'),

    # path('hashtag/', HashTagList.as_view(), name='hashtags'),
]