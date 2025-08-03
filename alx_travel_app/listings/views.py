# listings/views.py

from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticated

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
