import os.path
from django.contrib.auth.models import User
from django.urls import include, path
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, URLPatternsTestCase, APIClient
from api_clients.models import Profile, Avatar
from apptrix.settings import MEDIA_ROOT

TEST_PASSWORD = 'zero'


class APPTRIXAPIRoutesTests(APITestCase, URLPatternsTestCase):
    first_user = None
    second_user = None
    urlpatterns = [
        path('api/', include("api_clients.urls")),
    ]
    
    def setUp(self) -> None:
        self.client = APIClient()
        first_user = User.objects.create(
            username='Orlov_Nikita',
            first_name='Nikita',
            last_name='Orlov',
            email='orlov@nikita.ru',
        )
        first_user.set_password(TEST_PASSWORD)
        first_user.save()
        self.first_user = first_user
        Profile.objects.create(
            user=self.first_user,
            sex='Men',
            avatar=Avatar.objects.create(src=os.path.join(MEDIA_ROOT, 'test', 'test_avatar_1.jpg'),
                                         alt='My avatar')
        )
        
        second_user = User.objects.create(
            username='Olga_Ivanova',
            first_name='Olga',
            last_name='Ivanova',
            email='olga@ivanova.ru',
        )
        second_user.set_password(TEST_PASSWORD)
        second_user.save()
        self.second_user = second_user
        Profile.objects.create(
            user=self.second_user,
            sex='Women',
            avatar=Avatar.objects.create(src=os.path.join(MEDIA_ROOT, 'test', 'test_avatar_2.jpg'),
                                         alt='My avatar')
        )
        Token.objects.create(user_id=first_user.id)
        Token.objects.create(user_id=second_user.id)
    
    def tearDown(self) -> None:
        for i in Avatar.objects.all():
            try:
                os.remove(os.path.join(MEDIA_ROOT, str(i.src).replace('/', '\\')))
            except FileNotFoundError:
                continue
