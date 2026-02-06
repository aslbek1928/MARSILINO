from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import Restaurant, Cashier
from .serializers import (
    RestaurantListSerializer, 
    RestaurantDetailSerializer,
    CashierLoginSerializer,
    CashierInfoSerializer,
    CashierCreateSerializer,
    CashierPINResetSerializer
)
from .tokens import CashierToken
from accounts.permissions import IsRestaurantAdmin

class RestaurantListView(generics.ListAPIView):
    """
    GET /api/restaurants/
    Public endpoint - list all restaurants with basic info.
    Supports search and hashtag filtering.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'hashtags', 'description']

class RestaurantDetailView(generics.RetrieveAPIView):
    """
    GET /api/restaurants/{id}/
    Public endpoint - get full restaurant details.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class CashierLoginView(APIView):
    """
    POST /api/cashier/auth/login/
    Cashier login using restaurant_id, phone_number, and PIN.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CashierLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        restaurant_id = serializer.validated_data['restaurant_id']
        phone_number = serializer.validated_data['phone_number']
        pin_code = serializer.validated_data['pin_code']
        
        # Find cashier
        try:
            cashier = Cashier.objects.get(
                restaurant_id=restaurant_id,
                phone_number=phone_number
            )
        except Cashier.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if active
        if not cashier.is_active:
            return Response(
                {"error": "Cashier account is disabled"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify PIN
        if not cashier.check_pin(pin_code):
            return Response(
                {"error": "Invalid PIN"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT token with cashier claims
        token = CashierToken.for_cashier(cashier)
        
        return Response({
            "cashier": CashierInfoSerializer(cashier).data,
            "access": str(token.access_token),
            "refresh": str(token),
        })


class CashierCreateView(APIView):
    """
    POST /api/restaurant-admin/cashiers/
    Create a new cashier (admin only). Returns the generated PIN once.
    """
    permission_classes = [IsRestaurantAdmin]

    def post(self, request):
        serializer = CashierCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate PIN
        raw_pin = Cashier.generate_pin(length=4)
        
        # Create cashier with hashed PIN
        cashier = Cashier(
            restaurant=serializer.validated_data['restaurant'],
            name=serializer.validated_data['name'],
            phone_number=serializer.validated_data['phone_number']
        )
        cashier.set_pin(raw_pin)
        cashier.save()
        
        return Response({
            "cashier": CashierInfoSerializer(cashier).data,
            "pin_code": raw_pin,  # Only shown once!
            "message": "Save this PIN - it will not be shown again."
        }, status=status.HTTP_201_CREATED)


class CashierPINResetView(APIView):
    """
    POST /api/restaurant-admin/cashiers/reset-pin/
    Reset a cashier's PIN (admin only). Returns the new PIN once.
    """
    permission_classes = [IsRestaurantAdmin]

    def post(self, request):
        serializer = CashierPINResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cashier_id = serializer.validated_data['cashier_id']
        cashier = get_object_or_404(Cashier, pk=cashier_id)
        
        # Generate new PIN
        raw_pin = Cashier.generate_pin(length=4)
        cashier.set_pin(raw_pin)
        cashier.save()
        
        return Response({
            "cashier": CashierInfoSerializer(cashier).data,
            "pin_code": raw_pin,  # Only shown once!
            "message": "New PIN generated. Save it - it will not be shown again."
        })


from rest_framework.permissions import IsAuthenticated
from .serializers import BookTableSerializer

class BookTableAPIView(APIView):
    """
    POST /api/restaurants/book-table/
    Book a table at a restaurant.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookTableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
