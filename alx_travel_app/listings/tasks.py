from celery import shared_task
from django.core.mail import send_mail
from .models import Payment

@shared_task
def send_payment_confirmation(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        booking = payment.booking

        send_mail(
            "Booking Payment Confirmation",
            f"Hello {booking.user.get_full_name()},\n\n"
            f"Your payment for booking {booking.reference} was successful.\n\n"
            "Thank you for choosing our service!",
            "no-reply@travelapp.com",
            [booking.user.email],
            fail_silently=False,
        )
    except Payment.DoesNotExist:
        # Optional: log error
        pass
