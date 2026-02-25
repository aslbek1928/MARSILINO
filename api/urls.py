from django.urls import path, include
from .views import (
    TagListView, RestaurantListView, WalletView, WalletAddView, 
    WalletTransferView, ReceiptVerifyView, MeView, 
    WalletTransactionListView, LikedRestaurantView, FCMDeviceView
)

v1_patterns = [
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
    path('v1/', include(v1_patterns)),
    # Fallback/Legacy paths if needed, but the user wants v1
    path('tags', TagListView.as_view()),
    path('restaurants', RestaurantListView.as_view()),
    path('wallet', WalletView.as_view()),
    path('wallet/add', WalletAddView.as_view()),
    path('wallet/transfer', WalletTransferView.as_view()),
    path('receipt/verify', ReceiptVerifyView.as_view()),
    path('me', MeView.as_view()),
]
