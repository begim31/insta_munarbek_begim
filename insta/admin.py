from django.contrib import admin

from .models import (Post, UserProfile, FavouritePost, Comment, Follow, Tag, Image)


admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Tag)
admin.site.register(FavouritePost)
admin.site.register(Follow)
admin.site.register(Comment)
