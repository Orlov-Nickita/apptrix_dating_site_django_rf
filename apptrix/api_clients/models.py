import os.path
from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
import os
from apptrix.settings import STATIC_ROOT


def make_watermark(img: Image) -> Image:
    """
    Функция для наложения водяного знака на аватар пользователя
    :param img: открытая картинка, которая требует наложения водяного знака, в PIL.Image.open()
    :return: Объект Image, содержащий совмещенную исходную картинку и водяной знак
    """
    
    watermark = Image.open(os.path.join(STATIC_ROOT, 'api_clients', 'watermark', 'water.png'))
    
    # Получаем размеры изображений
    img_width: int = img.size[0]
    img_height: int = img.size[1]
    
    # Растягиваем водяной знак до размеров изображения
    watermark = watermark.resize((img_width, img_height))
    
    # Создаем объект для наложения водяного знака
    image_with_watermark: Image = Image.new(mode='RGBA', size=img.size, color=(0, 0, 0, 0))
    image_with_watermark.paste(im=img, box=(0, 0))
    
    # Наложение водяного знака на изображение
    image_with_watermark.paste(im=watermark, box=(0, 0), mask=watermark)
    
    return image_with_watermark


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
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Переопределенный метод сохранения аватара пользователя. Перед сохранением накладывается водяной знак, а далее
        сохраняется в БД и присваивается пользователю.
        :param force_insert: Используется для создания новых объектов в базе данных.
        :param force_update: Используется для обновления уже существующих объектов в базе данных.
        :param using: По умолчанию используется база данных по умолчанию.
        :param update_fields: Список полей, которые нужно обновить при сохранении объекта. Если этот параметр не
        указан, то будут обновлены все поля объекта. Этот параметр может использоваться для оптимизации работы с
        базой данных.
        :return: Объект модели Аватар сохраняется в БД.
        """
        img: Image = Image.open(self.src)
        
        if hasattr(img, '_getexif'):
            exifdata = img._getexif()
            if exifdata:
                orientation = exifdata.get(274)
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        
        img: Image = make_watermark(img)
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        self.src = InMemoryUploadedFile(buffer, None, self.src.name, 'image/png', buffer.tell(), None)
        
        return super().save(force_insert, force_update, using, update_fields)


class Profile(models.Model):
    """
    Модель Профиль
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='пользователь')
    sex = models.CharField(max_length=20, verbose_name='пол')
    avatar = models.OneToOneField(Avatar, on_delete=models.CASCADE, verbose_name='аватар')
    longitude = models.DecimalField(decimal_places=8, max_digits=12, verbose_name='долгота местоположения', default=0,
                                    null=True)
    latitude = models.DecimalField(decimal_places=8, max_digits=12, verbose_name='широта местоположения', default=0,
                                   null=True)
    
    class Meta:
        """
        Метакласс для определения названий в единственном и множественном числе
        """
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        """
        Строка с никнеймом пользователя
        """
        return '{}{}'.format('Доп.инфо пользователя ', self.user.username)


class Like(models.Model):
    """
    Модель Симпатии
    """
    like_from_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='симпатия от пользователя',
                                       related_name='like_from_user')
    like_to_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='симпатия пользователю',
                                     related_name='like_to_user')
    
    class Meta:
        """
        Метакласс для определения названий в единственном и множественном числе
        """
        verbose_name = 'Симпатия'
        verbose_name_plural = 'Симпатии'
    
    def __str__(self):
        """
        Строка с симпатиями между пользователями
        """
        return f'like: {self.like_from_user.first_name} -> {self.like_to_user.first_name}'
