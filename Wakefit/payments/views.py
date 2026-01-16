from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
import asyncio
from django.http import JsonResponse

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny]) # UroPay doesn't have your JWT token, so we allow any
def uropay_webhook(request):
    """
    This is where the ngrok tunnel leads.
    UroPay calls this when the user pays.
    """
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


# PRD Section 15: Non-blocking Async View
async def async_payment_status(request, transaction_id):
    """
    Simulates checking a 3rd party API for payment status 
    without blocking the main Django thread.
    """
    # Simulate a network delay (like calling UroPay)
    await asyncio.sleep(1) 
    
    return JsonResponse({
        "transaction_id": transaction_id,
        "status": "Processing",
        "message": "This request was handled asynchronously!"
    })