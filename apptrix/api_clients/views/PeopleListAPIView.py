from django.contrib.auth.models import User
from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from geopy.distance import geodesic
from api_clients.models import Profile
from api_clients.serializiers import UserSerializer
from apptrix.settings import logger


class PeopleAPIViewPagination(PageNumberPagination):
    """
    Пагинация для списка пользователей
    """
    page_size_query_param = 'limit'


class PeopleListAPIViewFilter(FilterSet):
    """
    Фильтрация списка пользователей по имени, фамилии и полу
    """
    first_name = CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = CharFilter(field_name='last_name', lookup_expr='icontains')
    sex = CharFilter(field_name='profile__sex', lookup_expr='iexact')
    distance = NumberFilter(method='distance_filter')
    
    def distance_filter(self, queryset, name, value):
        """
        Фильтрует queryset по заданному расстоянию - исключает из выборки тех пользователей, кто находится дальше
        обозначенного расстояния value
        """
        user: Profile = Profile.objects.get(user_id=self.request.user.id)
        # profiles_within_distance = Profile.objects.annotate(
        #     distance=geodesic(
        #         (user.latitude, user.longitude),
        #         (F('latitude'), F('longitude'))
        #     )
        # ).filter(distance__lte=value)
        
        queryset = queryset.exclude(id=user.id)
        for i in queryset:
            if geodesic((user.latitude, user.longitude), (i.profile.latitude, i.profile.longitude)).kilometers > value:
                queryset = queryset.exclude(id=i.id)
        
        return queryset
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'sex', 'distance']


class PeopleListAPIView(ListAPIView):
    """
    Представление для получения списка всех пользователей сайта
    """
    filterset_class = PeopleListAPIViewFilter
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
