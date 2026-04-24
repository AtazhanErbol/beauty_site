from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from .models import Service, Advantage, FAQ, Booking, PortfolioItem
from .forms import ContactForm, BookingForm
from .utils import (
    get_day_slots, send_booking_notifications,
    send_contact_notification, build_whatsapp_booking_link,
)


def _get_common_context():
    return {
        'services': Service.objects.filter(is_active=True),
        'advantages': Advantage.objects.filter(is_active=True),
        'faqs': FAQ.objects.filter(is_active=True),
        'portfolio_items': PortfolioItem.objects.filter(is_active=True),
    }


@ratelimit(key='ip', rate='10/m', method='POST', block=False)
def index(request):
    """Главная одностраничная страница."""
    # Rate-limit: не более 10 POST-запросов/минуту с одного IP
    was_limited = getattr(request, 'limited', False)

    if request.method == 'POST':
        if was_limited:
            messages.error(
                request,
                'Слишком много попыток отправки формы. Пожалуйста, попробуйте позже.'
            )
            form = ContactForm()
        else:
            form = ContactForm(request.POST)
            if form.is_valid():
                # Сохраняем только нужные поля модели (не капчу/honeypot)
                contact = form.save()
                send_contact_notification(contact)
                messages.success(
                    request,
                    'Спасибо! Ваша заявка отправлена. '
                    'Мы свяжемся с вами в ближайшее время.'
                )
                return redirect(reverse('index') + '#contact')
            else:
                messages.error(request, 'Проверьте правильность заполнения формы.')
    else:
        form = ContactForm()

    context = _get_common_context()
    context['contact_form'] = form
    return render(request, 'main/index.html', context)


@ratelimit(key='ip', rate='20/m', method='POST', block=False)
def booking_page(request):
    """Страница онлайн-записи."""
    was_limited = getattr(request, 'limited', False)

    services = Service.objects.filter(is_active=True)
    preselected_service_id = request.GET.get('service')

    initial = {}
    if preselected_service_id:
        try:
            initial['service'] = int(preselected_service_id)
        except (ValueError, TypeError):
            pass

    if request.method == 'POST':
        if was_limited:
            messages.error(
                request,
                'Слишком много попыток записи. Пожалуйста, попробуйте через минуту.'
            )
            form = BookingForm(initial=initial)
        else:
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save()
                send_booking_notifications(booking)
                try:
                    from .telegram_bot import send_telegram_booking
                    send_telegram_booking(booking)
                except Exception as e:
                    print(f'Telegram ошибка: {e}')
                whatsapp_link = build_whatsapp_booking_link(booking)
                return render(request, 'main/booking_success.html', {
                    'booking': booking,
                    'whatsapp_link': whatsapp_link,
                })
            else:
                messages.error(
                    request,
                    'Пожалуйста, проверьте корректность данных и выбранный слот.'
                )
    else:
        form = BookingForm(initial=initial)

    today = timezone.localdate()
    max_date = today + timedelta(days=settings.BOOKING_DAYS_AHEAD)

    context = {
        'form': form,
        'services': services,
        'today': today.isoformat(),
        'max_date': max_date.isoformat(),
        'days_ahead': settings.BOOKING_DAYS_AHEAD,
        'slot_interval': settings.BOOKING_SLOT_INTERVAL_MINUTES,
    }
    return render(request, 'main/booking.html', context)


@require_GET
@ratelimit(key='ip', rate='60/m', block=True)
def api_slots(request):
    """API: возвращает список слотов на указанную дату."""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Параметр date обязателен'}, status=400)

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Неверный формат даты (YYYY-MM-DD)'}, status=400)

    today = timezone.localdate()
    max_date = today + timedelta(days=settings.BOOKING_DAYS_AHEAD)

    if target_date < today or target_date > max_date:
        return JsonResponse({'slots': [], 'date': date_str})

    slots = get_day_slots(target_date)

    slots_data = [
        {
            'time': s['time'],
            'available': s['available'],
            'reason': s['reason'],
        }
        for s in slots
    ]

    return JsonResponse({
        'slots': slots_data,
        'date': date_str,
    })


def handler404(request, exception):
    return render(request, 'main/404.html', status=404)


def handler403(request, exception):
    return render(request, 'main/404.html', status=403)


def ratelimited_view(request, exception=None):
    return render(request, 'main/404.html', {
        'error_title': 'Слишком много запросов',
        'error_message': 'Пожалуйста, попробуйте позже.',
    }, status=429)

