#type:ignore
# from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# from django.views.decorators.http import sync_and_async_middleware
from .models import Payment
import asyncio
from django.http import JsonResponse
from asgiref.sync import sync_to_async

@method_decorator(csrf_exempt, name='dispatch')
class UroPayWebhookView(APIView):
    """
    Class-based API view for payment gateway callbacks.

    HTTP Method: POST (UroPay sends payment status updates via POST requests)

    This is where the ngrok tunnel leads.
    UroPay calls this when the user pays.
    """
    permission_classes = [AllowAny]

    """Handle POST requests from payment gateway"""
    def post(self, request):
        """Handle POST requests from payment gateway"""
        # 1. Log the data (Check your terminal to see the payload!)
        print(f"WEBHOOK RECEIVED: {request.data}")

        # 2. Identify the order (UroPay sends 'merchantOrderId' back)
        order_id = request.data.get('merchantOrderId')
        status = request.data.get('status') # Assuming 'SUCCESS' or 'PAID'

        if status == 'SUCCESS':
            try:
                payment = Payment.objects.get(order__order_id=order_id)
                payment.status = 'completed'
                payment.save()

                order = payment.order
                order.status = 'paid'
                order.save()
                return Response({"status": "Success updated"}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response({"status": "ignored"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentStatusView(APIView):
    """
    Async class-based view to fetch payment status.
    
    HTTP Method: GET (Client polls this endpoint to check payment status)
    
    Uses async operations to query the database and simulate network latency
    without blocking the main Django thread.
    """
    permission_classes = [AllowAny]
    
    async def get(self, request, transaction_id):
        """
        Handle GET requests to fetch payment status.
        
        Args:
            request: Django request object
            transaction_id: Transaction ID to lookup payment status
        
        Returns:
            JsonResponse with payment status data
        """
        # Simulate network delay when querying external payment provider
        await asyncio.sleep(1)
        
        try:
            # Query actual payment from database (async-safe)
            payment = await sync_to_async(Payment.objects.get)(transaction_id=transaction_id)
            
            return JsonResponse({
                "transaction_id": transaction_id,
                "status": payment.status,  # Returns actual status: 'pending', 'completed', 'failed'
                "amount": str(payment.amount),
                "provider": payment.provider,
                "created_at": payment.created_at.isoformat(),
                "message": "Payment status fetched successfully"
            })
        except Payment.DoesNotExist:
            return JsonResponse({
                "transaction_id": transaction_id,
                "status": "not_found",
                "message": "No payment record found with this transaction ID"
            }, status=404)