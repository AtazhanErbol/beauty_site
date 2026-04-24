import requests
from urllib.parse import quote
from django.conf import settings


def send_telegram_booking(booking):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    # Ссылка на WhatsApp с готовым сообщением клиенту
    whatsapp_message = (
        f"Здравствуйте, {booking.name}! "
        f"Ваша запись подтверждена. "
        f"Услуга: {booking.service}. "
        f"Дата: {booking.date.strftime('%d.%m.%Y')}. "
        f"Время: {booking.time.strftime('%H:%M')}. "
        f"Ждём вас!"
    )
    phone = booking.phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    whatsapp_link = f"https://wa.me/{phone}?text={quote(whatsapp_message)}"

    text = (
        f"📅 Новая запись!\n\n"
        f"👤 Имя: {booking.name}\n"
        f"📞 Телефон: {booking.phone}\n"
        f"💅 Услуга: {booking.service}\n"
        f"📅 Дата: {booking.date.strftime('%d.%m.%Y')}\n"
        f"🕐 Время: {booking.time.strftime('%H:%M')}\n\n"
        f"✅ Нажми чтобы подтвердить клиенту в WhatsApp:\n{whatsapp_link}"
    )

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )
