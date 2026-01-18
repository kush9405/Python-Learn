#type:ignore
from payments.services import initiate_uropay_order
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import (OrderCreateSerializer, OrderHistorySerializer,OrderItemSerializer)
from .services import CheckoutData, OrderItemDTO, checkout_orchestrator


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
        try:
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
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging
            logger = logging.getLogger('orders')
            logger.error(f"Unexpected checkout error: {e}")
            return Response({"error": "Internal Server Error"}, status=500)




class OrderHistoryAPIView(generics.ListAPIView):
    """
    PRD Section 4 & 7: Only authenticated users can see their own data.
    """
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Crucial Security Move: Filter orders by the logged-in user
        # We also use 'prefetch_related' to speed up the query (Optimized ORM)
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product').order_by('-created_at')