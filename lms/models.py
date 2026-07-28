from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    preview = models.ImageField(
        upload_to="lms/course_previews/",
        verbose_name="Превью (картинка)",
        blank=True,
        null=True,
    )
    description = models.TextField(verbose_name="Описание курса", blank=True, null=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Lesson(models.Model):
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

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.title
