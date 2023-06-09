from django.urls import path
from rest_framework.authtoken import views
from api_clients.views import RegistrationView, MatchView, PeopleView

app_name = 'api_clients'

urlpatterns = [
    path('clients/create/', RegistrationView.as_view(), name='client_create'),
    path('clients/<int:user_id>/match/', MatchView.as_view(), name='client_match'),
    path('list/', PeopleView.as_view(), name='list_people'),
    path('api-token-auth/', views.obtain_auth_token),
]
