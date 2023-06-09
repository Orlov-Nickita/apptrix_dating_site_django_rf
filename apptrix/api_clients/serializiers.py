from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api_clients.models import Profile, Avatar


class AvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Avatar
    """
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        """
        Метакласс для определения модели и полей модели, с которыми будет работать сериализатор
        """
        model = Avatar
        fields = ['id', 'src', 'alt']


class ShortProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Profile - короткая версия
    """
    avatar = AvatarSerializer()
    
    class Meta:
        """
        Метакласс для определения модели и полей модели, с которыми будет работать сериализатор
        """
        model = Profile
        fields = ['sex', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User
    """
    id = serializers.IntegerField(read_only=True)
    profile = ShortProfileSerializer()
    
    class Meta:
        """
        Метакласс для определения модели и полей модели, с которыми будет работать сериализатор
        """
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Profile
    """
    user = UserSerializer(read_only=True)
    avatar = AvatarSerializer()
    
    class Meta:
        """
        Метакласс для определения модели и полей модели, с которыми будет работать сериализатор
        """
        model = Profile
        fields = ['user', 'sex', 'avatar']
    
    def create(self, validated_data):
        return Profile.objects.create(
            user_id=validated_data.get('user_id'),
            avatar=Avatar.objects.create(**validated_data.get('avatar')),
            sex=validated_data.get('sex'),
        )


class SetPasswordSerializer(serializers.Serializer):
    """
    Сериализатор для создания пароля
    """
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise ValidationError("Пароли не совпадают")
        return attrs
