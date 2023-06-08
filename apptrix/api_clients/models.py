from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from apptrix.settings import MEDIA_ROOT


def make_watermark(img: Image) -> Image:
    """
    TODO
    :param img:
    :return:
    """
    watermark = Image.open(f'{MEDIA_ROOT}water.png')
    
    # Получаем размеры изображений
    img_width, img_height = img.size
    
    # Растягиваем водяной знак до размеров изображения
    watermark = watermark.resize((img_width, img_height))

    # Создаем объект для наложения водяного знака
    image_with_watermark = Image.new(mode='RGBA', size=img.size, color=(0, 0, 0, 0))
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
        img: Image = Image.open(self.src)
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
