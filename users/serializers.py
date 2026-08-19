from rest_framework import serializers

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("user", "payment_link", "session_id")


class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["email", "phone", "city", "avatar", "payments"]
        read_only_fields = ["email"]


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей.
    Проверяет обязательное наличие email и пароля, а также скрывает пароль в ответах API.
    """

    class Meta:
        model = User
        fields = ["email", "password", "phone", "city", "avatar"]
        extra_kwargs = {
            "password": {"write_only": True},
        }


class UserPublicProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра ЧУЖИХ профилей (скрыты платежи, пароль, фамилия)."""

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar"]
