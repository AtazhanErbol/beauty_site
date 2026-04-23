"""Формы проекта.

ContactForm / BookingForm — публичные формы с защитой от спама:
  - honeypot-поле (скрыто от людей, видно ботам);
  - капча-вопрос (простая математическая задача);
  - серверная валидация имени/телефона/даты/времени.
"""
import random
from django import forms
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import Booking, ContactRequest, Service


# ---------------------------------------------------------------------------
#  Миксины защиты
# ---------------------------------------------------------------------------

class HoneypotMixin(forms.Form):
    """Ловушка для ботов: скрытое поле, которое никогда не должно быть заполнено."""
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
            'style': 'position:absolute;left:-9999px;top:-9999px;opacity:0;'
                    'pointer-events:none;height:0;width:0;',
        }),
        label='Не заполняйте это поле',
    )

    def clean_website(self):
        value = self.cleaned_data.get('website', '')
        if value:
            # Ловушка сработала — это бот
            raise forms.ValidationError('Ошибка отправки формы.')
        return value


class CaptchaMixin(forms.Form):
    """Простая арифметическая капча.

    Вопрос и правильный ответ хранятся в двух полях формы:
      - captcha_question (hidden) — текст вопроса;
      - captcha_answer — поле, куда пользователь вводит результат.
    Защита от подмены question: второе поле captcha_token хранит
    подписанный hash ожидаемого ответа.
    """
    captcha_question = forms.CharField(
        widget=forms.HiddenInput(), required=True
    )
    captcha_token = forms.CharField(
        widget=forms.HiddenInput(), required=True
    )
    captcha_answer = forms.CharField(
        label='Антиспам',
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Результат',
            'autocomplete': 'off',
            'inputmode': 'numeric',
        }),
        help_text='Решите простой пример, чтобы подтвердить, что вы не робот.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если форма создаётся без данных — генерируем новую капчу
        if not self.is_bound:
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            question = f'{a} + {b}'
            answer = a + b
            self.fields['captcha_question'].initial = question
            self.fields['captcha_token'].initial = self._make_token(answer)
            self.fields['captcha_answer'].label = f'Сколько будет {question}?'
        else:
            question = self.data.get('captcha_question', '')
            if question:
                self.fields['captcha_answer'].label = f'Сколько будет {question}?'

    @staticmethod
    def _make_token(answer: int) -> str:
        from django.core.signing import Signer
        return Signer(salt='captcha').sign(str(answer))

    @staticmethod
    def _unsign_token(token: str):
        from django.core.signing import Signer, BadSignature
        try:
            return int(Signer(salt='captcha').unsign(token))
        except (BadSignature, ValueError):
            return None

    def clean(self):
        cleaned = super().clean()
        token = cleaned.get('captcha_token', '')
        answer_raw = cleaned.get('captcha_answer', '')
        expected = self._unsign_token(token) if token else None

        if expected is None:
            self.add_error('captcha_answer',
                           'Срок действия капчи истёк, обновите страницу.')
            return cleaned
        try:
            given = int(str(answer_raw).strip())
        except (TypeError, ValueError):
            self.add_error('captcha_answer', 'Введите число.')
            return cleaned
        if given != expected:
            self.add_error('captcha_answer', 'Неверный ответ, попробуйте ещё раз.')
        return cleaned


# ---------------------------------------------------------------------------
#  ContactForm
# ---------------------------------------------------------------------------

class ContactForm(HoneypotMixin, CaptchaMixin, forms.ModelForm):
    """Форма обратной связи с honeypot и капчей."""
    class Meta:
        model = ContactRequest
        fields = ['name', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше имя',
                'required': True,
                'maxlength': 100,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+7 (___) ___-__-__',
                'required': True,
                'maxlength': 30,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше сообщение',
                'rows': 4,
                'required': True,
                'maxlength': 2000,
            }),
        }

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Имя должно содержать минимум 2 символа')
        if len(name) > 100:
            raise forms.ValidationError('Имя слишком длинное')
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона')
        if len(digits) > 15:
            raise forms.ValidationError('Номер телефона слишком длинный')
        return phone

    def clean_message(self):
        msg = (self.cleaned_data.get('message') or '').strip()
        if len(msg) < 3:
            raise forms.ValidationError('Сообщение слишком короткое')
        if len(msg) > 2000:
            raise forms.ValidationError('Сообщение слишком длинное (максимум 2000 символов)')
        # Примитивная защита от ссылок-спама
        if msg.lower().count('http') > 3:
            raise forms.ValidationError('Слишком много ссылок в сообщении')
        return msg


# ---------------------------------------------------------------------------
#  BookingForm
# ---------------------------------------------------------------------------

class BookingForm(HoneypotMixin, forms.ModelForm):
    """Форма онлайн-записи. Капча не нужна — и так многоэтапная форма."""
    class Meta:
        model = Booking
        fields = ['name', 'phone', 'service', 'date', 'time', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше имя',
                'required': True,
                'maxlength': 100,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+7 (___) ___-__-__',
                'required': True,
                'maxlength': 30,
            }),
            'service': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'date': forms.HiddenInput(),
            'time': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Комментарий (необязательно)',
                'rows': 3,
                'maxlength': 1000,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['service'].empty_label = 'Выберите услугу'
        self.fields['comment'].required = False

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Имя должно содержать минимум 2 символа')
        if len(name) > 100:
            raise forms.ValidationError('Имя слишком длинное')
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона')
        if len(digits) > 15:
            raise forms.ValidationError('Номер телефона слишком длинный')
        return phone

    def clean_date(self):
        d = self.cleaned_data.get('date')
        if not d:
            raise forms.ValidationError('Выберите дату записи')
        today = timezone.localdate()
        if d < today:
            raise forms.ValidationError('Нельзя записаться на прошедшую дату')
        max_date = today + timedelta(days=settings.BOOKING_DAYS_AHEAD)
        if d > max_date:
            raise forms.ValidationError(
                f'Запись возможна максимум на {settings.BOOKING_DAYS_AHEAD} дней вперёд'
            )
        return d

    def clean_time(self):
        t = self.cleaned_data.get('time')
        if not t:
            raise forms.ValidationError('Выберите время записи')
        return t

    def clean_comment(self):
        c = (self.cleaned_data.get('comment') or '').strip()
        if len(c) > 1000:
            raise forms.ValidationError('Комментарий слишком длинный (максимум 1000 символов)')
        return c

    def clean(self):
        cleaned = super().clean()
        d = cleaned.get('date')
        t = cleaned.get('time')

        if d and t:
            # Проверка на прошедшее время
            slot_dt = datetime.combine(d, t)
            now = timezone.localtime().replace(tzinfo=None)
            if slot_dt < now:
                raise forms.ValidationError('Нельзя записаться на прошедшее время')

            # Проверка занятости (учитываем интервал между записями)
            interval = timedelta(minutes=settings.BOOKING_SLOT_INTERVAL_MINUTES)

            active_bookings = Booking.objects.filter(
                date=d
            ).exclude(status='cancelled')

            for b in active_bookings:
                existing_dt = datetime.combine(b.date, b.time)
                delta = abs((slot_dt - existing_dt).total_seconds())
                if delta < interval.total_seconds():
                    raise forms.ValidationError(
                        'Это время уже занято или слишком близко к другой записи. '
                        'Пожалуйста, выберите другой слот.'
                    )

        return cleaned
