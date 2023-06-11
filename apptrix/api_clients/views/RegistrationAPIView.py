from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.request import Request
from rest_framework.response import Response
from api_clients.serializiers import UserSerializer, RegProfileSerializer, SetPasswordSerializer
from apptrix.settings import logger


class RegistrationAPIView(CreateAPIView):
    """
    Представление для регистрации пользователей
    """
    parser_classes = [MultiPartParser, FileUploadParser]
    authentication_classes = []
    permission_classes = []
    
    def post(self, request: Request, *args, **kwargs):
        """
        Отправка формы с данными пользователя для регистрации нового пользователя и получения аутентификационного
        токена для дальнейшей работы
        """
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
        ps = RegProfileSerializer(data=user_profile)
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
                    
                    logger.info('Зарегистрирован новый пользователь',
                                username=f'{a.username}, id={a.id}')
                    return Response(data=data, status=status.HTTP_201_CREATED)
                
                logger.error(f'Произошла ошибка {ps.errors} при валидации данных профиля',
                             username=f'{user["username"]}, {user["email"]}')
                return Response(ps.errors, status=status.HTTP_400_BAD_REQUEST)
            
            logger.error(f'Произошла ошибка {us.errors} при валидации данных пользователя',
                         username=f'{user["username"]}, {user["email"]}')
            return Response(us.errors, status=status.HTTP_400_BAD_REQUEST)
        
        logger.error(f'Произошла ошибка {upass.errors} при валидации пароля',
                     username=f'{user["username"]}, {user["email"]}')
        return Response(upass.errors, status=status.HTTP_400_BAD_REQUEST)
