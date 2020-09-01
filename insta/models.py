from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    avatar = models.ImageField(upload_to='avatars', default='images/avatars/no_photo.jpeg')

    def __str__(self):
        return f"{self.user.username}'s profile"



class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    images = models.ManyToManyField('Image')
    description = models.TextField()
    tags = models.ManyToManyField('Tag', blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        posts = list(Post.objects.filter(author=self.author))
        index = posts.index(self)
        return f"{self.author.username}'s Post #{index+1}"


class Image(models.Model):
    image = models.ImageField(upload_to='images/post_images')


class Tag(models.Model):
    title = models.SlugField(max_length=100, primary_key=True)

    def __str__(self):
        return self.title


class FavouritePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')

    def __str__(self):
        return f"{self.user.username} LIKES {self.post}"


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f"{self.follower.username} FOLLOWS {self.user.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return f"{self.author.username}'s COMMENT on {self.post}"

#
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)





