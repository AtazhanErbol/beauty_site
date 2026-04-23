from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import (
    SiteSettings, Service, Advantage, FAQ,
    Booking, ContactRequest, PortfolioItem,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = (
        ('Hero-блок', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'hero_video_file')
        }),
        ('Информация о мастере', {
            'fields': ('master_name', 'work_hours')
        }),
        ('Контакты', {
            'fields': ('phone', 'whatsapp', 'instagram', 'email', 'address')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords')
        }),
    )

    def has_add_permission(self, request):
        # Только одна запись настроек
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('title', 'price', 'duration_minutes', 'order', 'is_active')
    list_editable = ('order', 'is_active', 'price')
    list_filter = ('is_active',)
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'id')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'is_active', 'order')
        }),
        ('Описание', {
            'fields': ('short_description', 'description')
        }),
        ('Детали', {
            'fields': ('price', 'duration_minutes', 'icon', 'image')
        }),
    )


@admin.register(Advantage)
class AdvantageAdmin(ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')


@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    list_display = (
        'name', 'phone', 'service', 'date', 'time',
        'status_badge', 'created_at'
    )
    list_filter = ('status', 'service', 'date')
    search_fields = ('name', 'phone')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Клиент', {
            'fields': ('name', 'phone')
        }),
        ('Запись', {
            'fields': ('service', 'date', 'time', 'status', 'comment')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Статус')
    def status_badge(self, obj):
        colors = {
            'new': '#3498db',
            'confirmed': '#27ae60',
            'completed': '#95a5a6',
            'cancelled': '#e74c3c',
        }
        color = colors.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; '
            'border-radius:10px; font-size:12px;">{}</span>',
            color, obj.get_status_display()
        )


@admin.register(ContactRequest)
class ContactRequestAdmin(ModelAdmin):
    list_display = ('name', 'phone', 'short_message', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'phone', 'message')
    list_editable = ('is_processed',)
    readonly_fields = ('created_at',)

    @admin.display(description='Сообщение')
    def short_message(self, obj):
        return obj.message[:80] + ('…' if len(obj.message) > 80 else '')


@admin.register(PortfolioItem)
class PortfolioItemAdmin(ModelAdmin):
    list_display = (
        'thumbnail', 'display_title', 'service',
        'order', 'is_active', 'created_at'
    )
    list_display_links = ('thumbnail', 'display_title')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'service')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'preview')

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'service')
        }),
        ('Изображение', {
            'fields': ('image', 'preview')
        }),
        ('Отображение', {
            'fields': ('order', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Превью')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;object-fit:cover;'
                'border-radius:6px;" alt="">',
                obj.image.url
            )
        return '—'

    @admin.display(description='Превью в админке')
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;'
                'border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.15);" alt="">',
                obj.image.url
            )
        return '—'
