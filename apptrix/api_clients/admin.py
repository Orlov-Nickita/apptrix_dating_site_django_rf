from django.contrib import admin

from api_clients.models import Avatar, Profile, Like


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ['id', 'src', 'alt', 'created_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'sex', 'avatar', 'longitude', 'latitude']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['like_from_user', 'like_to_user']
