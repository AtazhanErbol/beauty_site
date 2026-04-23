from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, FileExtensionValidator
from django.utils import timezone
from django.urls import reverse


phone_validator = RegexValidator(
    regex=r'^\+?[0-9\s\-\(\)]{7,20}$',
    message='Введите корректный номер телефона'
)

image_extension_validator = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']
)


class SiteSettings(models.Model):
    """Общие настройки сайта (редактируются в админке)."""
    master_name = models.CharField(
        'Имя мастера', max_length=100, default='Мастер Анна'
    )
    hero_title = models.CharField(
        'Заголовок Hero', max_length=200,
        default='Подчеркни свою красоту'
    )
    hero_subtitle = models.CharField(
        'Подзаголовок Hero', max_length=300,
        default='Наращивание ресниц и ламинирование бровей — с заботой о каждой детали'
    )
    hero_image = models.ImageField(
        'Картинка Hero', upload_to='hero/', blank=True, null=True,
        validators=[image_extension_validator],
        help_text='Рекомендуемый размер: 1920×1080 и больше'
    )
    hero_video_file = models.FileField(
    'Видео-файл Hero', upload_to='hero/video/', blank=True, null=True,
    validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])],
    help_text='Загрузите MP4/WebM файл. Если загружен файл — он приоритетнее ссылки.'
    )
    
    phone = models.CharField(
        'Телефон', max_length=30, default='+7 (999) 000-00-00',
        validators=[phone_validator]
    )
    whatsapp = models.CharField(
        'WhatsApp (номер без +)', max_length=30, default='79990000000',
        help_text='Только цифры, без +, пробелов и скобок. Например: 79990000000'
    )
    instagram = models.CharField(
        'Instagram (логин без @)', max_length=100, default='beauty_master',
        blank=True
    )
    address = models.CharField(
        'Адрес', max_length=300,
        default='г. Москва, ул. Пример, д. 1'
    )
    email = models.EmailField(
        'Email для уведомлений', default='master@example.com'
    )

    work_hours = models.CharField(
        'Часы работы', max_length=100, default='Пн–Вс: 09:00–21:00'
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    def save(self, *args, **kwargs):
        # Синглтон: только одна запись
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    seo_title = models.CharField('SEO заголовок', max_length=60, blank=True)
    seo_description = models.TextField('SEO описание', max_length=160, blank=True)
    seo_keywords = models.CharField('Ключевые слова', max_length=300, blank=True)

class Service(models.Model):
    """Услуга мастера."""
    title = models.CharField('Название услуги', max_length=150)
    slug = models.SlugField('URL-slug', max_length=150, unique=True)
    short_description = models.CharField(
        'Краткое описание', max_length=300
    )
    description = models.TextField('Полное описание', blank=True)
    price = models.DecimalField(
        'Цена (₽)', max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    duration_minutes = models.PositiveIntegerField(
        'Длительность (мин.)', default=150,
        help_text='Примерная длительность процедуры'
    )
    image = models.ImageField(
        'Изображение', upload_to='services/', blank=True, null=True,
        validators=[image_extension_validator]
    )
    icon = models.CharField(
        'Иконка (Font Awesome класс)', max_length=100,
        default='fa-solid fa-eye',
        help_text='Например: fa-solid fa-eye, fa-solid fa-feather'
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Advantage(models.Model):
    """Блок преимущества мастера."""
    title = models.CharField('Заголовок', max_length=150)
    description = models.CharField('Описание', max_length=300)
    icon = models.CharField(
        'Иконка (Font Awesome класс)', max_length=100,
        default='fa-solid fa-star'
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Преимущество'
        verbose_name_plural = 'Преимущества'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """Часто задаваемые вопросы."""
    question = models.CharField('Вопрос', max_length=300)
    answer = models.TextField('Ответ')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос (FAQ)'
        verbose_name_plural = 'FAQ — Часто задаваемые вопросы'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question


class Booking(models.Model):
    """Запись клиента."""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]

    name = models.CharField('Имя клиента', max_length=100)
    phone = models.CharField(
        'Телефон', max_length=30, validators=[phone_validator]
    )
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT,
        related_name='bookings', verbose_name='Услуга'
    )
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='new'
    )

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-date', '-time']
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'time'],
                condition=~models.Q(status='cancelled'),
                name='unique_active_booking_slot'
            )
        ]

    def __str__(self):
        return f'{self.name} — {self.service} — {self.date} {self.time}'

    @property
    def datetime(self):
        from datetime import datetime
        return datetime.combine(self.date, self.time)

    @property
    def is_past(self):
        return self.datetime < timezone.now().replace(tzinfo=None)


class ContactRequest(models.Model):
    """Заявка через форму обратной связи."""
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField(
        'Телефон', max_length=30, validators=[phone_validator]
    )
    message = models.TextField('Сообщение')
    is_processed = models.BooleanField('Обработано', default=False)

    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки с формы обратной связи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.phone} ({self.created_at:%d.%m.%Y %H:%M})'


class PortfolioItem(models.Model):
    """Работа мастера в портфолио.

    Изображения загружаются через админку и отображаются на главной
    в блоке «Портфолио». Клик по работе открывает её в lightbox-модалке.
    """
    title = models.CharField(
        'Название работы', max_length=150, blank=True,
        help_text='Необязательно. Отображается над описанием.'
    )
    description = models.CharField(
        'Короткое описание', max_length=300, blank=True,
        help_text='Необязательно. Показывается в lightbox.'
    )
    image = models.ImageField(
        'Изображение', upload_to='portfolio/',
        validators=[image_extension_validator],
        help_text='JPG, PNG, WEBP (до 5 МБ).'
    )
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL,
        related_name='portfolio_items',
        verbose_name='Связанная услуга', null=True, blank=True,
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать на сайте', default=True)

    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Работа (портфолио)'
        verbose_name_plural = 'Портфолио — работы мастера'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f'Работа #{self.pk}'

    @property
    def display_title(self):
        return self.title or 'Работа мастера'
