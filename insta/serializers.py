from .functions import validateEmail
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Post, FavoritesPosts, Comments, Followers
from django.shortcuts import get_object_or_404


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
        fields = ['image', 'description', 'comments']

    def to_representation(self, instance):
        representation = super(PostSerializer, self).to_representation(instance)
        representation['author'] = instance.user.username
        representation['likes'] = instance.likes.count()
        representation['id'] = instance.id
        representation['comments'] = CommentsSerializer(instance.comments, many=True).data
        return representation


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
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(CommentsSerializer, self).to_representation(instance)
        representation = representation.get('description')
        return representation



class FollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers
        fields = ['followers',]


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        representation['post'] = PostSerializer(instance.user.posts, many=True).data
        return representation
