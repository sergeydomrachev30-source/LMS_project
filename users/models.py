from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для управления пользователями (User).
    Позволяет создавать обычных и суперпользователей, используя email вместо стандартного username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя с указанным email и паролем.
        Принудительно нормализует email и хэширует пароль перед сохранением в БД.
        """
        if not email:
            raise ValueError("Email является обязательным полем")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя (администратора) с указанным email и паролем.
        Принудительно выставляет флаги административного доступа (is_staff=True, is_superuser=True).
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь статус сотрудника.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь статус суперпользователя.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя учебной платформы.
    Убирает стандартное поле username. В качестве главного идентификатора (логина) используется email.
    Хранит контактные данные (телефон, город) и аватар пользователя.
    """

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
        """
        Возвращает текстовое представление пользователя в виде его email-адреса.
        """
        return self.email


class Payment(models.Model):
    """
    Модель для фиксации финансовых операций (платежей) на платформе.
    Связана с пользователем, совершившим платеж, и конкретной сущностью (курсом или уроком).
    Хранит дату операции, сумму и выбранный способ оплаты.
    """

    PAYMENT_METHODS = [("cash", "Наличные"), ("transfer", "Перевод на счет")]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="payments",
    )
    payment_date = models.DateTimeField(verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        "lms.Course",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Оплаченный курс",
    )
    paid_lesson = models.ForeignKey(
        "lms.Lesson",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Оплаченный урок",
    )
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, verbose_name="Способ оплаты"
    )

    payment_link = models.TextField(
        blank=True, null=True, verbose_name="Ссылка на оплату"
    )
    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии"
    )

    PAYMENT_STATUSES = [
        ("unpaid", "В процессе оплаты"),
        ("paid", "Оплачено"),
    ]

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUSES,
        default="unpaid",
        verbose_name="Статус платежа",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        """
        Возвращает текстовое описание платежа, содержащее email плательщика и способ оплаты.
        """
        return f"{self.user} - {self.payment_method}"
