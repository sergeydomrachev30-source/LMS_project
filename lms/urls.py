from django.urls import path
from rest_framework.routers import SimpleRouter

from .apps import LmsConfig
from .views import (CourseViewSet, LessonCreateAPIView, LessonDestroyAPIView,
                    LessonListAPIView, LessonRetrieveAPIView,
                    LessonUpdateAPIView)

app_name = LmsConfig.name

# 1. Сначала создаем роутер и РЕГИСТРИРУЕМ в нем ViewSet
router = SimpleRouter()
router.register(r"courses", CourseViewSet, basename="courses")

# 2. Создаем список обычных путей для уроков
urlpatterns = [
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-get"),
    path(
        "lessons/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"
    ),
    path(
        "lessons/delete/<int:pk>/", LessonDestroyAPIView.as_view(), name="lesson-delete"
    ),
]

urlpatterns += router.urls
