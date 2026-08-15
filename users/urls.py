from django.urls import path

from .apps import UsersConfig
from .views import (
    PaymentListAPIView,
    UserProfileUpdateAPIView,
    UserRegisterCreateAPIView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserRegisterCreateAPIView.as_view(), name="register"),
    path(
        "profile/update/<int:pk>/",
        UserProfileUpdateAPIView.as_view(),
        name="profile-update",
    ),
    path(
        "payments/",
        PaymentListAPIView.as_view(),
        name="payment-list",
    ),
]
