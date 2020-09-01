from .functions import validateEmail
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Post, FavouritePost, Comment, Follow, Tag, Image
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

    def __get_image_url(self, instance):
        request = self.context.get('request')
        if instance.userprofile.avatar:
            url = instance.userprofile.avatar.url
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.userprofile is None:
            UserProfile.objects.create(user=instance)
        representation['avatar'] = self.__get_image_url(instance)
        if self.context.get('action') == 'detail':
            followings_object_list = instance.followers.filter(follower=instance)
            followings_list = [follow.user.username for follow in followings_object_list]
            representation['following'] = followings_list
            followers_object_list = instance.followings.filter(user=instance)
            followers_list = [follow.follower.username for follow in followers_object_list]
            representation['followers'] = followers_list
            representation['posts'] = PostSerializer(instance.posts, many=True, context=self.context).data
        else:
            representation['posts'] = instance.posts.count()
            representation['followers'] = instance.followings.count()
            representation['following'] = instance.followers.count()
        return representation


class UserProfileSerializer(serializers.ModelSerializer):
    # user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    class Meta:
        model = UserProfile
        fields = ['id', 'avatar']

    def create(self, validated_data):
        user = self.context.get('request').user
        if UserProfile.objects.filter(user=user).exists():
            userprofile = UserProfile.objects.get(user=user)
            userprofile.delete()
        userprofile = UserProfile.objects.create(user=user, **validated_data)
        return userprofile


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    avatar = serializers.ImageField(allow_empty_file=True, write_only=True, default='images/avatars/no_photo.jpeg')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'avatar']

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
        if validated_data['avatar']:
            avatar = validated_data['avatar']
            userProfile = UserProfile(user=user, avatar=avatar)
        else:
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
                user_request = get_object_or_404(User, email=email_or_username,)
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
    id = serializers.HyperlinkedRelatedField(read_only=True, view_name='post_detail')
    author = serializers.StringRelatedField(read_only=True)
    image = serializers.ListField(write_only=True)
    tag = serializers.ListField(max_length=100, write_only=True, default='')
    pub_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'author', 'description', 'image', 'tag', 'pub_date']

    def create(self, validated_data):
        description = validated_data['description']
        images_list = validated_data.pop('image')
        tags_list = validated_data.pop('tag')
        user = self.context.get('request').user
        post = Post(description=description, author=user)
        post.save()
        for tag in tags_list:
            if Tag.objects.filter(title=tag).exists():
                post.tags.add(tag)
            else:
                post.tags.create(title=tag)
        [post.images.create(image=image) for image in images_list]
        return post

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'tag':
                tags = instance.tags.all()
                tags.delete()
                for tag in value:
                    if Tag.objects.filter(title=tag).exists():
                        instance.tags.add(tag)
                    else:
                        instance.tags.create(title=tag)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


    def to_representation(self, instance):
        representation = super(PostSerializer, self).to_representation(instance)
        representation['images'] = ImageSerializer(instance.images, many=True).data
        pub_date = representation.pop('pub_date')
        if self.context.get('action') == 'detail':
            representation.pop('id')
            representation['pub_date'] = pub_date
            representation['likes'] = instance.likes.count()
            representation['tags'] = TagSerializer(instance.tags, many=True).data
            representation['comments'] = CommentSerializer(instance.comments, many=True).data
        return representation


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']

    def __get_image_url(self, instance):
        request = self.context.get('request')
        if instance.image:
            url = instance.image.url
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = self.__get_image_url(instance)
        return representation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation = representation['title']
    #     return representation


class FavouritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouritePost
        fields = ['post']

    def create(self, validated_data):
        post = validated_data.get('post')
        user = self.context['request'].user

        if FavouritePost.objects.filter(post=post, user=user).exists():
            msg = "This post has already been liked"
            raise serializers.ValidationError(msg)
        else:

            FavoritePost = FavouritePost.objects.create(
                post=post,
                user=user
            )

            FavoritePost.save()

            return FavoritePost


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    pub_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S', read_only=True)
    class Meta:
        model = Comment
        fields = ['description', 'post', 'author', 'pub_date']

    def create(self, validated_data):
        comment = Comment(author=self.context.get('request').user, **validated_data)
        comment.save()
        return comment


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


