from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from lms.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """
    Отправляет email-уведомления всем подписчикам курса при его обновлении.
    """
    course = Course.objects.get(pk=course_id)

    email_list = [
        subscription.user.email
        for subscription in Subscription.objects.filter(course=course)
    ]

    if email_list:
        send_mail(
            subject=f'Обновление курса "{course.title}"',
            message=f'Привет! В курсе "{course.title}" произошли изменения.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=email_list,
            fail_silently=False,
        )
        print(f"Уведомления об обновлении курса {course_id} отправлены.")
