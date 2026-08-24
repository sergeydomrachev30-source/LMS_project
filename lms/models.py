from django.conf import settings
from django.db import models


class Course(models.Model):
    """
    Модель курса учебной платформы.
    Хранит информацию о названии, описании, обложке и авторе (владельце) курса.
    Связана с моделью уроков (Lesson) обратной связью 'lessons'.
    """

    title = models.CharField(max_length=200, verbose_name="Название курса")
    preview = models.ImageField(
        upload_to="lms/course_previews/",
        verbose_name="Превью (картинка)",
        blank=True,
        null=True,
    )
    description = models.TextField(verbose_name="Описание курса", blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        """
        Возвращает текстовое представление курса в виде его названия.
        Используется в админ-панели Django и логах.
        """
        return self.title


class Lesson(models.Model):
    """
    Модель урока, входящего в состав курса.
    Хранит текстовые материалы, ссылку на видео, обложку и данные о владельце.
    Каждый урок обязательно привязан к одному конкретному курсу.
    """

    title = models.CharField(max_length=150, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока", blank=True, null=True)
    preview = models.ImageField(
        upload_to="lms/lesson_previews/",
        verbose_name="Превью (картинка)",
        blank=True,
        null=True,
    )
    video_url = models.URLField(verbose_name="Ссылка на видео", blank=True, null=True)

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец урока",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        """
        Возвращает текстовое представление урока в виде его названия.
        Используется в админ-панели Django и логах.
        """
        return self.title


class Subscription(models.Model):
    """
    Модель подписки пользователя на конкретный курс.
    Используется для отслеживания интереса пользователя к контенту и управления уведомлениями.
    Связка (user, course) является уникальной, чтобы избежать дублирования подписок.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="subscriptions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="subscriptions",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = (("user", "course"),)
