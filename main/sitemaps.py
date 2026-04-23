from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['index']

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return f'/#services'