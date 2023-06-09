from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api_clients.models import Like
from api_clients.serializiers import UserSerializer, ProfileSerializer, SetPasswordSerializer


class RegistrationView(CreateAPIView):
    """
    TODO
    """
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


class MatchView(APIView):
    """
    TODO
    """
    
    def get(self, request: Request, user_id: int):
        match, created = Like.objects.get_or_create(like_from_user=request.user,
                                                    like_to_user_id=user_id)
        
        try:
            second_side = Like.objects.get(like_from_user_id=user_id,
                                           like_to_user=request.user)
        except ObjectDoesNotExist:
            second_side = None
        
        if not created:
            return Response(data={"detail": "You have already sent a sympathy to this user"},
                            status=status.HTTP_200_OK)
        
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
            
            return Response(data={"match": f"You have mutual sympathy! "
                                           "Rather, write to the mail to get to know each other better! "
                                           f"Sent HI-email for {second_side.like_from_user.first_name} to -> "
                                           f"{second_side.like_from_user.email}"},
                            status=status.HTTP_200_OK)
        
        return Response(data={"detail": "Sympathy sent to user"},
                        status=status.HTTP_201_CREATED)
