from rest_framework.generics import UpdateAPIView, ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Payment
from .serializers import UserProfileSerializer, PaymentSerializer


class UserProfileUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
