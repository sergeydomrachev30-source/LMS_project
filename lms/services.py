import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course_title):
    """
    Создает продукт в платежной системе Stripe на основе названия курса.
    Возвращает объект продукта, из которого мы сможем забрать его ID.
    """
    product = stripe.Product.create(
        name=course_title,
    )
    return product


def create_stripe_price(product_id, amount):
    """
    Создает цену в платежной системе Stripe для конкретного продукта.
    Сумма (amount) принимается в рублях и принудительно переводится в копейки.
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),
        currency="rub",
    )
    return price


def create_stripe_session(price_id):
    """
    Создает сессию оплаты в Stripe на основе ID цены.
    Возвращает объект сессии, содержащий ссылку на оплату (url).
    """
    session = stripe.checkout.Session.create(
        success_url=settings.STRIPE_SUCCESS_URL,  # Заменили хардкод на настройку
        cancel_url=settings.STRIPE_CANCEL_URL,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session


def retrieve_stripe_session(session_id):
    """
    Получает данные о сессии оплаты из Stripe по её идентификатору.
    Позволяет узнать актуальный статус платежа (payment_status).
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return session
