from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars', max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images', max_length=255, null=False)
    description = models.TextField()
    tags = models.ManyToManyField('Tag', blank=True)

    def __str__(self):
        return self.description

class Tag(models.Model):
    title = models.SlugField(max_length=100, primary_key=True)

class FavoritesPosts(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()


class FavoritesComments(models.Model):
    comment = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)