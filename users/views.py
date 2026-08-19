from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.filters import OrderingFilter
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveAPIView, RetrieveUpdateAPIView)
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from lms.services import (create_stripe_price, create_stripe_product,
                          create_stripe_session, retrieve_stripe_session)

from .models import Payment, User
from .serializers import (PaymentSerializer, UserProfileSerializer,
                          UserPublicProfileSerializer, UserRegisterSerializer)


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
        user: User = serializer.save()
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
        if getattr(self, "swagger_fake_view", False):
            return UserProfileSerializer
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


class PaymentCreateAPIView(CreateAPIView):
    """
    Контроллер для создания нового платежа в системе.
    Интегрирован со Stripe: автоматически создает продукт, цену и сессию оплаты,
    сохраняя ссылку на оплату в объекте платежа.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Перехватывает создание платежа, отправляет данные в Stripe,
        получает ссылку на оплату и привязывает платеж к текущему пользователю.
        """
        payment: Payment = serializer.save(user=self.request.user)

        if payment.paid_course:
            product_name = payment.paid_course.title
        elif payment.paid_lesson:
            product_name = payment.paid_lesson.title
        else:
            product_name = "Оплата обучения"

        stripe_product = create_stripe_product(product_name)
        stripe_price = create_stripe_price(stripe_product.id, payment.payment_amount)
        stripe_session = create_stripe_session(stripe_price.id)

        payment.payment_link = stripe_session.url
        payment.session_id = stripe_session.id
        payment.save()


class PaymentStatusRetrieveAPIView(RetrieveAPIView):
    """
    Контроллер для ручной проверки и обновления статуса платежа.
    Обращается в Stripe по session_id и синхронизирует статус в локальной БД.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="Уникальный числовой идентификатор платежа в системе",
                type=openapi.TYPE_INTEGER,
            )
        ]
    )
    def get_object(self):
        """
        Перехватывает получение объекта платежа, запрашивает статус из Stripe
        и обновляет его в нашей базе данных перед отдачей ответа.
        """
        payment = super().get_object()

        if payment.session_id:
            stripe_session = retrieve_stripe_session(payment.session_id)
            stripe_status = stripe_session.payment_status

            if stripe_status == "paid":
                payment.status = "paid"
            else:
                payment.status = "unpaid"

            payment.save()

        return payment
