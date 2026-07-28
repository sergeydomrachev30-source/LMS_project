from django.urls import path
from .apps import UsersConfig
from .views import UserProfileUpdateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path(
        "profile/update/<int:pk>/",
        UserProfileUpdateAPIView.as_view(),
        name="profile-update",
    ),
]
