from .functions import validateEmail
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Post, FavoritesPosts, Comments, Follow, Tag
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.followers.all().count() > 0:
            followings_object_list = instance.followers.filter(follower=instance)
            followings_list = [follow.user.username for follow in followings_object_list]
            representation['followings'] = followings_list
        if instance.followings.all().count() > 0:
            followers_object_list = instance.followings.filter(user=instance)
            followers_list = [follow.follower.username for follow in followers_object_list]
            representation['followers'] = followers_list
        return representation


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'passowrd': {'write_only': True}
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2')

        if password != password2:
            raise serializers.ValidationError('Passwords are diffrent')
        return data

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'])

        password = validated_data['password']
        user.set_password(password)
        user.save()

        # Create a profile for new user
        userProfile = UserProfile(user=user)
        userProfile.save()

        return user


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email_or_username = data.get('email_or_username')
        password = data.get('password')

        if email_or_username and password:

            if validateEmail(email_or_username):

                user_request = get_object_or_404(
                    User,
                    email=email_or_username,
                )

                email_or_username = user_request.username

            user = authenticate(username=email_or_username, password=password)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "email or username" and "password"'
            raise serializers.ValidationError(msg)

        data['user'] = user
        return data


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['image', 'description', 'tags']

    def to_representation(self, instance):
        representation = super(PostSerializer, self).to_representation(instance)
        representation['author'] = instance.user.username
        representation['likes'] = instance.likes.count()
        representation['id'] = instance.id

        return representation

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']

class FavoritesPostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoritesPosts
        fields = ['post']

    def create(self, validated_data):
        post = validated_data.get('post')
        user = self.context['request'].user

        if FavoritesPosts.objects.filter(post=post, user=user).exists():
            msg = "This post is already in favourites"
            raise serializers.ValidationError(msg)
        else:

            FavoritePost = FavoritesPosts.objects.create(
                post=post,
                user=user
            )

            FavoritePost.save()

            return FavoritePost


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['comments',]


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['user']

    def create(self, validated_data):
        user_to_follow = validated_data.get('user')
        user_who_is_following = self.context['request'].user

        if Follow.objects.filter(user=user_to_follow, follower=user_who_is_following).exists():
            msg = "This user is already followings"
            raise serializers.ValidationError(msg)
        elif user_who_is_following.id == user_to_follow.id:
            msg = "User cannot follow itself"
            raise serializers.ValidationError(msg)
        else:

            follow = Follow.objects.create(
                user=user_to_follow,
                follower=user_who_is_following
            )

            # follow.save()

            return follow
