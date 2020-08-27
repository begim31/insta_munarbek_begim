from django.contrib import admin
from .models import Post, UserProfile, FavoritesPosts, FavoritesComments, Comments, Follow, Tag

# Register your models here.
admin.site.register(Post)
admin.site.register(UserProfile)
admin.site.register(FavoritesPosts)
admin.site.register(FavoritesComments)
admin.site.register(Comments)
admin.site.register(Follow)
admin.site.register(Tag)