from rest_framework import serializers
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["email", "phone", "city", "avatar", "payments"]
        read_only_fields = ["email"]
