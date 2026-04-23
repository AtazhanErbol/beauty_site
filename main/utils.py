"""Вспомогательные функции для работы со слотами и уведомлениями."""
from datetime import datetime, date, time, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Booking, SiteSettings


def get_day_slots(target_date):
    """Возвращает список слотов на день с флагом доступности.

    Слоты формируются с интервалом BOOKING_SLOT_INTERVAL_MINUTES
    в рамках рабочего дня. Слот недоступен, если:
      - он в прошлом;
      - уже есть активная запись, пересекающаяся по интервалу.
    """
    interval = settings.BOOKING_SLOT_INTERVAL_MINUTES
    start_hour = settings.BOOKING_WORK_START_HOUR
    end_hour = settings.BOOKING_WORK_END_HOUR

    slots = []
    current = datetime.combine(target_date, time(start_hour, 0))
    end = datetime.combine(target_date, time(end_hour, 0))

    active_bookings = list(
        Booking.objects.filter(date=target_date).exclude(status='cancelled')
    )
    booked_datetimes = [
        datetime.combine(b.date, b.time) for b in active_bookings
    ]

    now = timezone.localtime().replace(tzinfo=None)

    while current < end:
        # По умолчанию доступен
        available = True
        reason = ''

        # Прошедшее время
        if current < now:
            available = False
            reason = 'past'

        # Пересечение с занятыми слотами (± интервал)
        if available:
            for bdt in booked_datetimes:
                if abs((current - bdt).total_seconds()) < interval * 60:
                    available = False
                    reason = 'booked'
                    break

        slots.append({
            'time': current.time().strftime('%H:%M'),
            'datetime': current,
            'available': available,
            'reason': reason,
        })
        current += timedelta(minutes=interval)

    return slots


def send_booking_notifications(booking):
    """Отправить уведомления о новой записи (email)."""
    site = SiteSettings.load()

    # Email клиенту (если указан)
    subject = f'Новая запись: {booking.service.title}'
    message = (
        f'Здравствуйте, {booking.name}!\n\n'
        f'Ваша запись успешно создана:\n'
        f'• Услуга: {booking.service.title}\n'
        f'• Дата: {booking.date.strftime("%d.%m.%Y")}\n'
        f'• Время: {booking.time.strftime("%H:%M")}\n'
        f'• Адрес: {site.address}\n\n'
        f'Если возникнут вопросы — звоните: {site.phone}\n\n'
        f'С уважением, {site.master_name}'
    )

    # Email администратору (мастеру)
    admin_message = (
        f'Новая запись на сайте!\n\n'
        f'Клиент: {booking.name}\n'
        f'Телефон: {booking.phone}\n'
        f'Услуга: {booking.service.title}\n'
        f'Дата: {booking.date.strftime("%d.%m.%Y")}\n'
        f'Время: {booking.time.strftime("%H:%M")}\n'
        f'Комментарий: {booking.comment or "—"}\n'
    )

    try:
        send_mail(
            subject=f'[Сайт] {subject}',
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[site.email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_contact_notification(contact_request):
    """Отправить уведомление о новой заявке."""
    site = SiteSettings.load()

    message = (
        f'Новая заявка с сайта!\n\n'
        f'Имя: {contact_request.name}\n'
        f'Телефон: {contact_request.phone}\n'
        f'Сообщение: {contact_request.message}\n'
    )

    try:
        send_mail(
            subject='[Сайт] Новая заявка с формы обратной связи',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[site.email],
            fail_silently=True,
        )
    except Exception:
        pass


def build_whatsapp_booking_link(booking):
    """Формирует ссылку wa.me для отправки подтверждения мастеру."""
    site = SiteSettings.load()
    text = (
        f'Здравствуйте! Я записался(-ась) на сайте:\n'
        f'Имя: {booking.name}\n'
        f'Услуга: {booking.service.title}\n'
        f'Дата: {booking.date.strftime("%d.%m.%Y")}\n'
        f'Время: {booking.time.strftime("%H:%M")}'
    )
    from urllib.parse import quote
    return f'https://wa.me/{site.whatsapp}?text={quote(text)}'
