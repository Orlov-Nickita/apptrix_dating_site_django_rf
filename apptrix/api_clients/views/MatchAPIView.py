from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from api_clients.models import Like
from apptrix.settings import logger


class MatchAPIView(APIView):
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
