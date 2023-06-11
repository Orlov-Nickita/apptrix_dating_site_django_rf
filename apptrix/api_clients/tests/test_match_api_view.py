from rest_framework import status
from rest_framework.reverse import reverse
from django.core import mail
from api_clients.tests.set_up import APPTRIXAPIRoutesTests, TEST_PASSWORD


class TestPeopleListAPIView(APPTRIXAPIRoutesTests):
    def test_api_route_named__client_match__get_request_without_auth_permission(self):
        url = reverse('api_clients:client_match', kwargs={'user_id': 2})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue('Учетные данные не были предоставлены' in response.data['detail'])
    
    def test_api_route_named__client_match__get_request_with_auth_permission_first_time(self):
        get_token_url = reverse('api_clients:get_token')

        auth_data = {
            'username': self.first_user.username,
            'password': TEST_PASSWORD,
        }

        token = self.client.post(get_token_url, auth_data).data['token']
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}

        url = reverse('api_clients:client_match', kwargs={'user_id': self.second_user.id})
        response = self.client.get(url, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data, {'detail': 'Sympathy sent to user'})
    
    def test_api_route_named__client_match__get_request_with_auth_permission_double_time(self):
        get_token_url = reverse('api_clients:get_token')
        
        auth_data = {
            'username': self.first_user.username,
            'password': TEST_PASSWORD,
        }
        
        token = self.client.post(get_token_url, auth_data).data['token']
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        
        url = reverse('api_clients:client_match', kwargs={'user_id': self.second_user.id})
        self.client.get(url, format='json', **headers)
        response = self.client.get(url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_208_ALREADY_REPORTED)
        self.assertTrue(response.data, {'detail': 'You have already sent a sympathy to this user'})
    
    def test_api_route_named__client_match__get_request_with_auth_permission_mutual_sympathy(self):
        get_token_url = reverse('api_clients:get_token')
        
        auth_data_first_user = {
            'username': self.first_user.username,
            'password': TEST_PASSWORD,
        }
        fu_token = self.client.post(get_token_url, auth_data_first_user).data['token']
        fu_headers = {"HTTP_AUTHORIZATION": f"Token {fu_token}"}
        url = reverse('api_clients:client_match', kwargs={'user_id': self.second_user.id})
        self.client.get(url, format='json', **fu_headers)
        
        auth_data_second_user = {
            'username': self.second_user.username,
            'password': TEST_PASSWORD,
        }
        su_token = self.client.post(get_token_url, auth_data_second_user).data['token']
        su_headers = {"HTTP_AUTHORIZATION": f"Token {su_token}"}
        url = reverse('api_clients:client_match', kwargs={'user_id': self.first_user.id})
        response = self.client.get(url, format='json', **su_headers)
        
        self.assertListEqual([self.first_user.email, self.second_user.email],
                             ['orlov@nikita.ru', 'olga@ivanova.ru'])
        self.assertTrue(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject, 'Mutual sympathy on the dating site!')
        self.assertTrue(mail.outbox[0].body, 'You have mutual sympathy! Nikita and OlgaRather, write to '
                                             'the mail to get to know each other better!orlov@nikita.ru <--> '
                                             'olga@ivanova.ru')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data, {'match': 'You have mutual sympathy! Rather, write to the mail to get to know '
                                                 'each other better! Sent HI-email for Olga to -> olga@ivanova.ru'})