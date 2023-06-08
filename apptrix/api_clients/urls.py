from django.urls import path
from rest_framework.authtoken import views

from api_clients.views import RegistrationView

app_name = 'api_clients'

urlpatterns = [
    path('create/', RegistrationView.as_view(), name='client_create'),
    path('api-token-auth/', views.obtain_auth_token)
]
