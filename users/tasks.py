from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def check_inactive_users():
    """
    Периодическая задача для автоматической блокировки пользователей.
    Проверяет дату последнего входа (last_login) и, если пользователь
    не заходил на платформу более 30 дней, меняет флаг is_active на False.
    """
    cutoff_date = timezone.now() - timedelta(days=30)
    # 1. Фильтруем пользователей (last_login меньше, чем cutoff_date)
    inactive_users = User.objects.filter(last_login__lt=cutoff_date, is_active=True)
    # 2. Обновляем их статус батчем (сразу всех одной командой)
    count = inactive_users.update(is_active=False)

    print(f"Заблокировано неактивных пользователей: {count}")
