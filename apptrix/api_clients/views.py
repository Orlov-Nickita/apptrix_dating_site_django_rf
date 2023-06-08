from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.request import Request
from rest_framework.response import Response
from api_clients.serializiers import UserSerializer, ProfileSerializer, SetPasswordSerializer


class RegistrationView(CreateAPIView):
    parser_classes = [MultiPartParser, FileUploadParser]
    authentication_classes = []
    permission_classes = []
    
    def post(self, request: Request, *args, **kwargs):
        user: dict = {
            'username': request.data.get("username"),
            'first_name': request.data.get("first_name"),
            'last_name': request.data.get("last_name"),
            'email': request.data.get("email")
        }
        user_pass: dict = {
            'password1': request.data.get("password1"),
            'password2': request.data.get("password2"),
        }
        user_profile: dict = {
            'sex': request.data.get("sex"),
            'avatar': {
                'src': request.data.get("avatar_src"),
                'alt': request.data.get("avatar_alt"),
            }
        }
        us = UserSerializer(data=user)
        ps = ProfileSerializer(data=user_profile)
        upass = SetPasswordSerializer(data=user_pass)
        if upass.is_valid(raise_exception=True):
            if us.is_valid(raise_exception=True):
                if ps.is_valid(raise_exception=True):
                    a: User = us.save()
                    a.set_password(upass.data.get('password2'))
                    a.save()
                    token: Token = Token.objects.create(user=a)
                    ps.save(user_id=a.id)
                    
                    data: dict = {
                        "Your token for authentication": token.key,
                    }
                    return Response(data=data, status=status.HTTP_201_CREATED)
                return Response(ps.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(us.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(upass.errors, status=status.HTTP_400_BAD_REQUEST)

# Пример запроса через curl

# curl
# -X POST http://localhost:8000/api/clients/create/
# -H "Content-Type: multipart/form-data"
# -F "avatar_src=@C:\Users\Никита\Desktop\gangster.jpg"
# -F "avatar_alt=test"
# -F "username=Nikita"
# -F "first_name=Nikita"
# -F "last_name=Orlov"
# -F "email=t@t.ru"
# -F "sex=Men"
# -F "password1=zerozero1"
# -F "password2=zerozero1"

# Пример ответа

# {"Your token for authentication":"613b78cfc4ae67614ec43689e1400f0774f9c7cb"}
