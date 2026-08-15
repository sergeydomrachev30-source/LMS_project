from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson

User = get_user_model()


class LessonAndSubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@skypro.ru", password="testpassword"
        )
        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание",
            course=self.course,
            owner=self.user,
        )

        self.moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator_user = User.objects.create_user(
            email="moderator@skypro.ru", password="testpassword"
        )
        self.moderator_user.groups.add(self.moderator_group)

    def test_create_lesson(self):
        """Тест создания урока (Валидатор YouTube)"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-create")

        data = {
            "title": "Новый урок",
            "course": self.course.id,
            "video_url": "https://youtube.com",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_validation_error(self):
        """Тест ошибки валидации при отправке плохой ссылки"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-create")

        # Отправляем запрещенный google.com
        data = {
            "title": "Урок с плохой ссылкой",
            "course": self.course.id,
            "video_url": "https://google.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_delete(self):
        """Тест успешного удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-delete", kwargs={"pk": self.lesson.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_subscription_toggle(self):
        """Тест работы эндпоинта подписки (создание и удаление по очереди)"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:course_subscribe")
        data = {"course_id": self.course.id}

        # Шаг 1: Подписываемся
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Подписка добавлена")

        # Шаг 2: Отписываемся (повторный запрос)
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Подписка удалена")

    def test_list_lesson(self):
        """Тест получения списка уроков модератором"""
        # Авторизуем созданного модератора
        self.client.force_authenticate(user=self.moderator_user)

        url = reverse("lms:lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_lesson(self):
        """Тест получения одного конкретного урока"""
        self.client.force_authenticate(user=self.user)
        # Передаем PK нашего тестового урока в kwargs
        url = reverse("lms:lesson-get", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("title"), self.lesson.title)

    def test_update_lesson(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-update", kwargs={"pk": self.lesson.pk})
        # Передаем новые данные для изменения
        data = {"title": "Абсолютно новое название урока", "course": self.course.id}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("title"), "Абсолютно новое название урока")

    def test_list_course(self):
        """Тест получения списка курсов владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:courses-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_course(self):
        """Тест получения деталей конкретного курса"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:courses-detail", kwargs={"pk": self.course.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("title"), self.course.title)
