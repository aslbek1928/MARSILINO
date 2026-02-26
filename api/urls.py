from django.urls import path, include
from .views import (
    TagListView, RestaurantListView, WalletView, WalletAddView, 
    WalletTransferView, ReceiptVerifyView, MeView, 
    WalletTransactionListView, LikedRestaurantView, FCMDeviceView,
    RegisterView, HealthCheckView, OTPSendView, OTPVerifyView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

api_patterns = [
    path('health', HealthCheckView.as_view(), name='health-check'),
    path('register', RegisterView.as_view(), name='api-register'),
    path('registration', RegisterView.as_view()), # Alias
    path('otp/send', OTPSendView.as_view(), name='otp-send'),
    path('otp/verify', OTPVerifyView.as_view(), name='otp-verify'),
    path('signin', TokenObtainPairView.as_view(), name='api-signin'),
    path('login', TokenObtainPairView.as_view()), # Alias
    path('token/refresh', TokenRefreshView.as_view(), name='api-token-refresh'),
    
    path('tags', TagListView.as_view(), name='tag-list'),
    path('restaurants', RestaurantListView.as_view(), name='restaurant-list'),
    path('wallet', WalletView.as_view(), name='wallet'),
    path('wallet/transactions', WalletTransactionListView.as_view(), name='wallet-transactions'),
    path('wallet/add', WalletAddView.as_view(), name='wallet-add'),
    path('wallet/transfer', WalletTransferView.as_view(), name='wallet-transfer'),
    path('receipt/verify', ReceiptVerifyView.as_view(), name='receipt-verify'),
    path('me', MeView.as_view(), name='me'),
    path('me/liked-restaurants/<str:restaurant_id>/<str:action>/', LikedRestaurantView.as_view(), name='liked-restaurant'),
    path('me/device', FCMDeviceView.as_view(), name='device-registration'),
]

urlpatterns = [
    path('v1/', include(api_patterns)),
    # Fallback for root api access as requested by user's app
    path('', include(api_patterns)),
]
