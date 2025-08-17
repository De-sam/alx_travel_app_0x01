from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404
import requests, uuid

from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    API viewset for CRUD operations on Listings
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    """
    API viewset for CRUD operations on Bookings
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="initiate-payment")
    def initiate_payment(self, request, pk=None):
        """
        Initiate a payment for a booking
        """
        booking = get_object_or_404(Booking, pk=pk)
        tx_ref = str(uuid.uuid4())

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "amount": str(booking.amount),
            "currency": "ETB",
            "tx_ref": tx_ref,
            "callback_url": request.build_absolute_uri("/api/payments/verify/"),
            "return_url": request.build_absolute_uri("/payment-success/"),
            "customization[title]": "Travel Booking Payment",
            "customization[description]": f"Booking for {booking.destination}",
            "customer[email]": booking.user.email,
            "customer[name]": booking.user.get_full_name(),
        }

        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        res = requests.post(chapa_url, json=payload, headers=headers).json()

        if res.get("status") == "success":
            Payment.objects.create(
                booking=booking,
                transaction_id=tx_ref,
                amount=booking.amount,
                status="Pending",
            )
            return Response({"checkout_url": res["data"]["checkout_url"]}, status=200)

        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def verify_payment(request, tx_ref):
    """
    Verify a payment after Chapa redirects back
    """
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    verify_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    res = requests.get(verify_url, headers=headers).json()

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
        if res.get("status") == "success" and res["data"]["status"] == "success":
            payment.status = "Completed"
            payment.save()
            # TODO: trigger Celery email task
        else:
            payment.status = "Failed"
            payment.save()
        return Response({"payment_status": payment.status}, status=200)
    except Payment.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)
