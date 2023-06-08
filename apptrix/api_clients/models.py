from django.contrib.auth.models import User
from django.db import models


class Avatar(models.Model):
    """
    Модель Аватар
    """
    src = models.ImageField(upload_to='avatars/', verbose_name='аватар', default=None, null=True)
    alt = models.CharField(max_length=200, verbose_name='описание изображения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    
    class Meta:
        """
        Метакласс для определения названий в единственном и множественном числе
        """
        verbose_name = 'Аватарка'
        verbose_name_plural = 'Аватарки'
    

class Profile(models.Model):
    """
    Модель Профиль
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='пользователь')
    sex = models.CharField(max_length=20, verbose_name='пол')
    avatar = models.OneToOneField(Avatar, on_delete=models.CASCADE, verbose_name='аватар')
    
    class Meta:
        """
        Метакласс для определения названий в единственном и множественном числе
        """
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        """
        Возвращается строка с никнеймом пользователя
        """
        return '{}{}'.format('Доп.инфо пользователя ', self.user.username)
