from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django_filters import CharFilter
from django_filters.rest_framework import FilterSet
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api_clients.models import Like
from api_clients.serializiers import UserSerializer, ProfileSerializer, SetPasswordSerializer
from apptrix.settings import logger


class RegistrationView(CreateAPIView):
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


class MatchView(APIView):
    """
    Представление для отправки симпатии другому пользователю, ID которого указан в URL
    """
    
    def get(self, request: Request, user_id: int):
        """
        Отправка симпатии другому пользователю, ID которого указан в URL
        """
        try:
            User.objects.get(id=user_id)
        
        except ObjectDoesNotExist:
            logger.error(f'Ошибка при отправке симпатии несуществующему пользователю',
                         username=request.user.username)
            return Response(data={"error": "Not found requested user"},
                            status=status.HTTP_404_NOT_FOUND)
        
        match, created = Like.objects.get_or_create(like_from_user=request.user,
                                                    like_to_user_id=user_id)
        
        try:
            second_side = Like.objects.get(like_from_user_id=user_id,
                                           like_to_user=request.user)
        except ObjectDoesNotExist:
            second_side = None
        
        if not created:
            logger.info(f'Повторная отправка симпатии тому же пользователю',
                        username=request.user.username)
            return Response(data={"detail": "You have already sent a sympathy to this user"},
                            status=status.HTTP_208_ALREADY_REPORTED)
        
        if match and second_side:
            send_mail(
                subject=f'Mutual sympathy on the dating site!',
                message=f'You have mutual sympathy! '
                        f'{second_side.like_from_user.first_name} and {second_side.like_to_user.first_name}'
                        f'Rather, write to the mail to get to know each other better!'
                        f'{second_side.like_from_user.email} <--> {second_side.like_to_user.email}',
                from_email='adad@add.ru',
                recipient_list=[f'{second_side.like_from_user.email}', f'{second_side.like_to_user.email}'],
                fail_silently=False,
            )
            logger.info(f'Взаимная симпатия между пользователями '
                        f'id={second_side.like_from_user.id} и id={second_side.like_to_user.id}')
            logger.info(f'Отправлены письма на адреса '
                        f'{second_side.like_from_user.email} и {second_side.like_to_user.email}')
            
            return Response(data={"match": f"You have mutual sympathy! "
                                           "Rather, write to the mail to get to know each other better! "
                                           f"Sent HI-email for {second_side.like_from_user.first_name} to -> "
                                           f"{second_side.like_from_user.email}"},
                            status=status.HTTP_200_OK)
        
        logger.info(f'Успешная отправка симпатии пользователю',
                    username=request.user.username)
        return Response(data={"detail": "Sympathy sent to user"},
                        status=status.HTTP_201_CREATED)


class PeopleAPIViewPagination(PageNumberPagination):
    """
    Пагинация для списка пользователей
    """
    page_size_query_param = 'limit'


class PeopleViewFilter(FilterSet):
    """
    Фильтрация списка пользователей по имени, фамилии и полу
    """
    first_name = CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = CharFilter(field_name='last_name', lookup_expr='icontains')
    sex = CharFilter(field_name='profile__sex', lookup_expr='iexact')
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'sex']


class PeopleView(ListAPIView):
    """
    Представление для получения списка всех пользователей сайта
    """
    filterset_class = PeopleViewFilter
    queryset = User.objects.prefetch_related('profile').prefetch_related('profile__avatar').all()
    serializer_class = UserSerializer
    pagination_class = PeopleAPIViewPagination
    
    def get(self, request, *args, **kwargs):
        """
        Получение списка всех пользователей сайта
        """
        logger.info(f'Получен список пользователей',
                    username=request.user.username)
        return self.list(request, *args, **kwargs)
