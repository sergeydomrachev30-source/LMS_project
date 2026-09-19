from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class BaseSecurityTestCase(APITestCase):
    def test_api_root_or_login_status(self):
        """Проверяем, что эндпоинт логина или главной страницы отвечает корректно"""
        try:
            url = reverse("token_obtain_pair")
        except:
            url = "/"

        response = self.client.get(url)

        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
