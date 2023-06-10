from django.urls import path
from django.views.generic import TemplateView
from rest_framework.authtoken import views
from api_clients.views import RegistrationView, MatchView, PeopleView

app_name = 'api_clients'

urlpatterns = [
    path('clients/create/', RegistrationView.as_view(), name='client_create'),
    path('clients/<int:user_id>/match/', MatchView.as_view(), name='client_match'),
    path('list/', PeopleView.as_view(), name='list_people'),
    path('api-token-auth/', views.obtain_auth_token),
    path('docs/', TemplateView.as_view(template_name='api_clients/swagger-ui.html',
                                       extra_context={'schema_url': 'openapi-schema'}),
         name='api_docs'),
]
