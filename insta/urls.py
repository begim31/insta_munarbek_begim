from django.urls import path
from .views import FavoritesPostsList, FavoritesPostsDestroy, CommentsList, FollowersList, UserDetails
from insta.views import UserRegister, CustomAuthToken, Logout, PostList, PostDetail, FavoritesPostsList

urlpatterns = [
    path('register/', UserRegister.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('posts/', PostList.as_view(), name='post_list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('favourites/', FavoritesPostsList.as_view(), name='favourites_list'),
    path('favourites/<pk>/', FavoritesPostsDestroy.as_view(), name='favourites_destroy'),
    path('comments/', CommentsList.as_view(), name='comments'),
    path('followers/', FollowersList.as_view(), name='followers'),
    path('users/<int:pk>/', UserDetails.as_view(), name='user_details'),
]