from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RequestOTPView, 
    VerifyOTPView, 
    RestaurantAdminLoginView,
    UserProfileView,
    LikedRestaurantView
)

urlpatterns = [
    # Mobile OTP Auth
    path('auth/request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Restaurant Admin Auth
    path('restaurant-admin/auth/login/', RestaurantAdminLoginView.as_view(), name='admin-login'),
    
    # User Profile
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/liked-restaurants/<uuid:restaurant_id>/<str:action>/', LikedRestaurantView.as_view(), name='liked-restaurant'),
]

