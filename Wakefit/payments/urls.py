#type:ignore
from django.urls import path
from .views import PaymentStatusView, UroPayWebhookView

urlpatterns = [
    path('webhook/', UroPayWebhookView.as_view(), name='uropay_webhook'),
    path('status/<str:transaction_id>/', PaymentStatusView.as_view(), name='payment_status'),
]