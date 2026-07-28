from rest_framework import serializers
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone", "city", "avatar"]
        read_only_fields = ["email"]
