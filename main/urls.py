from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('booking/', views.booking_page, name='booking'),
    path('api/slots/', views.api_slots, name='api_slots'),
]
