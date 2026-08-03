from django.urls import path
from .apps import UsersConfig
from .views import UserProfileUpdateAPIView, PaymentListAPIView

app_name = UsersConfig.name

urlpatterns = [
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
