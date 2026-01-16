from payments.services import initiate_uropay_order
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrderCreateSerializer, OrderItemSerializer
from .services import CheckoutData, OrderItemDTO, checkout_orchestrator


# orders/views.py
# orders/views.py
class PlaceOrderView(generics.GenericAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        # Build DTOs
        if vd.get('items'):
            items_dtos = [OrderItemDTO(**item) for item in vd['items']]
        else:
            items_dtos = [OrderItemDTO(product_id=vd['product_id'], quantity=vd['quantity'])]

        # Simple checkout data
        checkout_data = CheckoutData(
            user=request.user,
            items=items_dtos,
            address=vd['address']
        )
        
        order, payment_data = checkout_orchestrator(checkout_data)

        return Response({
            "order_id": order.order_id,
            "payment": payment_data,
            "message": "Order Placed! Check your email for confirmation."
        }, status=201)