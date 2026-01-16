from django.urls import path
from .views import async_payment_status, uropay_webhook

urlpatterns = [
    path('webhook/', uropay_webhook, name='uropay_webhook'),
    path('status/<str:transaction_id>/', async_payment_status, name='async_payment_status'),
]