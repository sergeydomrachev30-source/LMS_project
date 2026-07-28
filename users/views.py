from rest_framework.generics import UpdateAPIView
from .models import User
from .serializers import UserProfileSerializer


class UserProfileUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
