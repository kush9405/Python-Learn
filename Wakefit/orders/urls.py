from django.urls import path

from .views import OrderHistoryAPIView, PlaceOrderView

urlpatterns = [
    path('place-order/', PlaceOrderView.as_view(), name='place_order'),
    path('history/', OrderHistoryAPIView.as_view(), name='order-history'), # <--- New Path
]