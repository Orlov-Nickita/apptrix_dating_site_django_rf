import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.reverse import reverse
from api_clients.tests.set_up import APPTRIXAPIRoutesTests
from apptrix.settings import MEDIA_ROOT

TEST_PASSWORD = 'TestPass'
URL = reverse('api_clients:client_create')


class TestRegistrationAPIView(APPTRIXAPIRoutesTests):
    
    def test_api_route_named__client_create__post_request_right(self):
        with open(f'{MEDIA_ROOT}test/test_avatar_1.jpg', 'rb') as f:
            image = SimpleUploadedFile('test.jpg', f.read(), content_type='image/jpeg')
        
        data: dict = {
            'avatar_src': image,
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@test.ru',
            'sex': 'Men',
            'avatar_alt': 'Test Avatar descr',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
            'username': 'IVAN_petrov_1',
        }
        
        response = self.client.post(URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('Your token for authentication' in response.data)
        
        file_path = os.path.exists(f'{MEDIA_ROOT}avatars/test.jpg')
        self.assertTrue(file_path)
        os.remove(f'{MEDIA_ROOT}avatars/test.jpg')
    
    def test_api_route_named__client_create__post_request_the_same_username(self):
        with open(f'{MEDIA_ROOT}test/test_avatar_1.jpg', 'rb') as f:
            image = SimpleUploadedFile('test.jpg', f.read(), content_type='image/jpeg')
        
        data: dict = {
            'avatar_src': image,
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@test.ru',
            'sex': 'Men',
            'avatar_alt': 'Test Avatar descr',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
            'username': 'IVAN_petrov_1',
        }
        self.client.post(URL, data=data, format='multipart')
        
        data: dict = {
            'avatar_src': 'image',
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@test.ru',
            'sex': 'Men',
            'avatar_alt': 'Test Avatar descr',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
            'username': 'IVAN_petrov_1',
        }
        
        response = self.client.post(URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Пользователь с таким именем уже существует' in response.data['username'][0])
        
        file_path = os.path.exists(f'{MEDIA_ROOT}avatars/test.jpg')
        self.assertTrue(file_path)
        os.remove(f'{MEDIA_ROOT}avatars/test.jpg')
    
    def test_api_route_named__client_create__post_request_wrong_password(self):
        data: dict = {
            'avatar_src': 'image',
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@testru',
            'sex': 'Men',
            'avatar_alt': 'Test Avatar descr',
            'password1': TEST_PASSWORD,
            'password2': 'TEST_PASSWORD',
            'username': 'IVAN_petrov_2',
        }
        
        response = self.client.post(URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Пароли не совпадают' in response.data['non_field_errors'][0])
    
    def test_api_route_named__client_create__post_request_wrong_email(self):
        data: dict = {
            'avatar_src': 'image',
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@testru',
            'sex': 'Men',
            'avatar_alt': 'Test Avatar descr',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
            'username': 'IVAN_petrov_3',
        }
        
        response = self.client.post(URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Введите правильный адрес электронной почты' in response.data['email'][0])
    
    def test_api_route_named__client_create__post_request_wrong_avatar_file(self):
        data: dict = {
            'avatar_src': 'image',
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@test.ru',
            'sex': 'Men',
            'avatar_alt': 'Test Avatar descr',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
            'username': 'IVAN_petrov_4',
        }
        
        response = self.client.post(URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Загруженный файл не является корректным файлом' in response.data['avatar']['src'][0])
    
    def test_api_route_named__client_create__post_request_wrong_avatar_alt(self):
        with open(f'{MEDIA_ROOT}test/test_avatar_1.jpg', 'rb') as f:
            image = SimpleUploadedFile('test_avatar_1.jpg', f.read(), content_type='image/jpeg')
        
        data: dict = {
            'avatar_src': image,
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'test@test.ru',
            'sex': 'Men',
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
            'username': 'IVAN_petrov_5',
        }
        
        response = self.client.post(URL, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Это поле не может быть пустым' in response.data['avatar']['alt'][0])
        file_path = os.path.exists(f'{MEDIA_ROOT}avatars/test_avatar_1.jpg')
        self.assertTrue(file_path)
        os.remove(f'{MEDIA_ROOT}avatars/test_avatar_1.jpg')
