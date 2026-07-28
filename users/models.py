from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Кастомный менеджер для создания пользователей без username"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email является обязательным полем")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь статус сотрудника.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь статус суперпользователя.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=255, unique=True, verbose_name="Email")
    phone = models.CharField(
        max_length=35, verbose_name="Телефон", blank=True, null=True
    )
    city = models.CharField(max_length=255, verbose_name="Город", blank=True, null=True)
    avatar = models.ImageField(
        upload_to="users/avatar/", verbose_name="Аватар", blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
