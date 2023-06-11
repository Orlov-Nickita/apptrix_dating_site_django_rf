from rest_framework import status
from rest_framework.reverse import reverse
from api_clients.tests.set_up import APPTRIXAPIRoutesTests, TEST_PASSWORD


class TestPeopleListAPIView(APPTRIXAPIRoutesTests):
    def test_api_route_named__list_people__get_request_without_auth_permission(self):
        url = reverse('api_clients:list_people')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue('Учетные данные не были предоставлены' in response.data['detail'])
    
    def test_api_route_named__list_people__get_request_with_auth_permission(self):
        expected = [{'id': 1,
                     'username': 'Orlov_Nikita',
                     'first_name': 'Nikita',
                     'last_name': 'Orlov',
                     'email': 'orlov@nikita.ru',
                     'profile': {'sex': 'Men',
                                 'avatar': {'id': 1,
                                            'src': 'http://testserver/media/avatars/test_avatar_1.jpg',
                                            'alt': 'My avatar'},
                                 'longitude': 0.0,
                                 'latitude': 0.0}},
                    {'id': 2,
                     'username': 'Olga_Ivanova',
                     'first_name': 'Olga',
                     'last_name': 'Ivanova',
                     'email': 'olga@ivanova.ru',
                     'profile': {'sex': 'Women',
                                 'avatar': {'id': 2,
                                            'src': 'http://testserver/media/avatars/test_avatar_2.jpg',
                                            'alt': 'My avatar'},
                                 'longitude': 0.0,
                                 'latitude': 0.0}}]

        get_token_url = reverse('api_clients:get_token')
        
        auth_data = {
            'username': self.first_user.username,
            'password': TEST_PASSWORD,
        }
        
        token = self.client.post(get_token_url, auth_data).data['token']
        
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}

        url = reverse('api_clients:list_people')
        response = self.client.get(url, format='json', **headers)

        self.assertTrue(len(response.data), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
