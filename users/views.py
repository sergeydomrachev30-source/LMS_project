from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    UserProfileSerializer,
    UserPublicProfileSerializer,
    UserRegisterSerializer,
)


class UserRegisterCreateAPIView(CreateAPIView):
    """
    Контроллер для регистрации (создания) нового пользователя.
    Доступен для всех пользователей, включая неавторизованных.
    """

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        """
        Создает объект пользователя и принудительно хеширует его пароль
        перед сохранением в базу данных.
        """
        user = serializer.save()
        raw_password = self.request.data.get("password")
        if raw_password:
            user.set_password(raw_password)
            user.save()


class UserProfileUpdateAPIView(RetrieveUpdateAPIView):
    """
    Контроллер для просмотра и редактирования профиля пользователя.
    Доступен только авторизованным пользователям. Редактирование разрешено только владельцу.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """
        Переключает сериализатор в зависимости от автора запроса:
        - Если пользователь смотрит свой профиль: отдаются полные данные (включая платежи).
        - Если пользователь смотрит чужой профиль: отдается только открытая информация.
        """
        profile_owner = self.get_object()
        if self.request.user == profile_owner:
            return UserProfileSerializer
        return UserPublicProfileSerializer


class PaymentListAPIView(ListAPIView):
    """
    Контроллер для просмотра списка платежей.
    Поддерживает фильтрацию по курсу, уроку, способу оплаты и сортировку по дате.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
