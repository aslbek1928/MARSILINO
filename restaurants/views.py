from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

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
from .tokens import CashierToken
from accounts.permissions import IsRestaurantAdmin
from django.shortcuts import render
from .rap_views import get_admin_restaurant
from django.contrib.auth.decorators import login_required

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

@login_required(login_url='/login/')
def rap_page_view(request):
    """
    Server-side rendered page for Restaurant Admin Panel.
    Shows transaction data for the admin's restaurant.
    """
    restaurant = get_admin_restaurant(request.user)
    
    transactions = []
    total_revenue = 0
    total_discount = 0
    transaction_count = 0
    
    if restaurant:
        from transactions.models import Transaction
        from django.db.models import Sum, Count
        
        # Get recent transactions
        transactions = Transaction.objects.filter(
            restaurant=restaurant
        ).select_related('user', 'cashier').order_by('-created_at')[:50]
        
        # Get summary stats
        stats = Transaction.objects.filter(restaurant=restaurant).aggregate(
            total_revenue=Sum('sum_after_discount'),
            total_discount=Sum('discount_amount_uzs'),
            transaction_count=Count('id'),
            total_before_discount=Sum('sum_before_discount'),
        )
        total_revenue = stats['total_revenue'] or 0
        total_discount = stats['total_discount'] or 0
        transaction_count = stats['transaction_count'] or 0
        total_before_discount = stats['total_before_discount'] or 0
    else:
        total_before_discount = 0
    
    context = {
        'restaurant': restaurant,
        'transactions': transactions,
        'bookings': [],
        'cashiers': [],
        'total_revenue': total_revenue,
        'total_discount': total_discount,
        'total_before_discount': total_before_discount,
        'transaction_count': transaction_count,
    }
    
    if restaurant:
        from .models import BookTable, Cashier
        context['bookings'] = BookTable.objects.filter(restaurant=restaurant).select_related('user').order_by('-date', '-time')
        context['cashiers'] = Cashier.objects.filter(restaurant=restaurant).order_by('name')

    return render(request, 'restaurants/rap.html', context)


@login_required(login_url='/login/')
def update_booking_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    booking_id = data.get('booking_id')
    new_status = data.get('status')

    if new_status not in ('pending', 'reserved', 'cancelled'):
        return JsonResponse({'error': 'Invalid status'}, status=400)

    from .models import BookTable
    try:
        # Get restaurant for this admin
        admin_profile = RestaurantAdmin.objects.filter(user=request.user).select_related('restaurant').first()
        if not admin_profile:
            return JsonResponse({'error': 'Not a restaurant admin'}, status=403)

        booking = BookTable.objects.get(BTID=booking_id, restaurant=admin_profile.restaurant)
        booking.status = new_status
        booking.save(update_fields=['status'])
        return JsonResponse({'success': True, 'status': new_status})
    except BookTable.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)
