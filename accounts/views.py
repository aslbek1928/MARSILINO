from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from .models import CustomUser, RestaurantAdmin
from .serializers import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    RestaurantAdminLoginSerializer
)
from .services import OTPService
from restaurants.models import Restaurant

class RequestOTPView(APIView):
    """
    POST /api/auth/request-otp/
    Request an OTP for phone number login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        
        try:
            OTPService.generate_otp(phone_number)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        return Response(
            {"message": "OTP sent successfully"},
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp/
    Verify OTP and issue JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        
        success, message = OTPService.verify_otp(phone_number, code)
        
        if not success:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create user
        user, created = CustomUser.objects.get_or_create(
            phone_number=phone_number,
            defaults={'is_active': True}
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_new_user": created
        }, status=status.HTTP_200_OK)

class RestaurantAdminLoginView(APIView):
    """
    POST /api/restaurant-admin/auth/login/
    Login for restaurant admins using phone + password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RestaurantAdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=phone_number, password=password)
        
        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is a restaurant admin
        try:
            admin_profile = user.restaurant_admin_profile
        except RestaurantAdmin.DoesNotExist:
            if not user.is_superuser:
                return Response(
                    {"error": "Not a restaurant admin"},
                    status=status.HTTP_403_FORBIDDEN
                )
            admin_profile = None
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        
        if admin_profile:
            response_data["restaurant_id"] = str(admin_profile.restaurant.id)
            response_data["restaurant_name"] = admin_profile.restaurant.name
        
        return Response(response_data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    GET /api/me/ - Get current user's profile
    PATCH /api/me/ - Update current user's profile (full_name only)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)


class LikedRestaurantView(APIView):
    """
    POST /api/me/liked-restaurants/{restaurant_id}/add/ - Add to liked
    POST /api/me/liked-restaurants/{restaurant_id}/remove/ - Remove from liked
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, restaurant_id, action):
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        
        if action == 'add':
            request.user.liked_restaurants.add(restaurant)
            message = f"Added {restaurant.name} to liked restaurants"
        elif action == 'remove':
            request.user.liked_restaurants.remove(restaurant)
            message = f"Removed {restaurant.name} from liked restaurants"
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "message": message,
            "liked_restaurants": list(request.user.liked_restaurants.values_list('id', flat=True))
        })
