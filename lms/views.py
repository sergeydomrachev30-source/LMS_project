from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Course, Lesson, Subscription
from .paginators import CustomPaginator
from .permissions import IsModerator, IsNotModerator, IsOwner
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(ModelViewSet):
    """
    ViewSet для работы с курсами.
    Обеспечивает CRUD-операции (создание, просмотр списка, просмотр деталей, обновление и удаление).
    Доступ к операциям разграничен в зависимости от роли пользователя (Владелец / Модератор).
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPaginator

    def perform_create(self, serializer):
        """
        Перехватывает процесс сохранения нового курса.
        Автоматически устанавливает текущего авторизованного пользователя в качестве владельца (owner).
        """
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """
        Динамически определяет права доступа в зависимости от текущего действия (action):
        - Создание (create) и удаление (destroy): разрешено только не-модераторам (IsNotModerator).
        - Просмотр (list, retrieve) и редактирование (update, partial_update): разрешено модераторам ИЛИ владельцам.
        """

        if self.action in ["create", "destroy"]:
            self.permission_classes = [IsNotModerator]
        elif self.action in ["retrieve", "list", "update", "partial_update"]:
            self.permission_classes = [IsModerator | IsOwner]
        return [permission() for permission in self.permission_classes]


class LessonCreateAPIView(CreateAPIView):
    """
    Контроллер для создания нового урока.
    Доступен только для пользователей, не являющихся модераторами.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        """
        Перехватывает процесс сохранения нового урока.
        Автоматически устанавливает текущего авторизованного пользователя в качестве владельца (owner).
        """
        serializer.save(owner=self.request.user)


class LessonListAPIView(ListAPIView):
    """
    Контроллер для просмотра списка всех уроков.
    Доступен только для модераторов (в текущей конфигурации прав).
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModerator]
    pagination_class = CustomPaginator


class LessonRetrieveAPIView(RetrieveAPIView):
    """
    Контроллер для детального просмотра одного конкретного урока по его ID.
    Доступен только модераторам или непосредственному владельцу урока.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModerator | IsOwner]


class LessonUpdateAPIView(UpdateAPIView):
    """
    Контроллер для редактирования данных урока.
    Доступен только модераторам или непосредственному владельцу урока.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModerator | IsOwner]


class LessonDestroyAPIView(DestroyAPIView):
    """
    Контроллер для удаления урока из базы данных.
    Доступен исключительно непосредственному владельцу урока.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner]


class SubscriptionAPIView(APIView):
    """
    Контроллер для управления подписками пользователей на курсы.
    Работает в режиме переключателя (toggle): включает или выключает подписку.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Управление подпиской: добавляет или удаляет подписку пользователя на курс.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course_id"],
            properties={
                "course_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID курса, на который оформляется или отменяется подписка",
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Успешное изменение статуса подписки",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Результат действия: "Подписка добавлена" или "Подписка удалена"',
                        )
                    },
                ),
            ),
            404: "Курс с указанным ID не найден",
        },
    )
    def post(self, *args, **kwargs):
        """
        Обрабатывает POST-запрос на изменение статуса подписки.
        Принимает JSON с полем course_id. Если подписка уже существует — удаляет её,
        если не существует — создает новую запись в базе данных.
        """
        user = self.request.user
        course_id = self.request.data.get("course_id")
        course_item = get_object_or_404(Course, pk=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)
        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"

        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"

        return Response({"message": message})
