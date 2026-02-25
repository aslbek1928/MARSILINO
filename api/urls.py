from django.urls import path
from .views import TagListView, RestaurantListView, WalletView, WalletAddView, WalletTransferView, ReceiptVerifyView, MeView

urlpatterns = [
    path('tags', TagListView.as_view(), name='tag-list'),
    path('restaurants', RestaurantListView.as_view(), name='restaurant-list'),
    path('wallet', WalletView.as_view(), name='wallet'),
    path('wallet/add', WalletAddView.as_view(), name='wallet-add'),
    path('wallet/transfer', WalletTransferView.as_view(), name='wallet-transfer'),
    path('receipt/verify', ReceiptVerifyView.as_view(), name='receipt-verify'),
    path('me', MeView.as_view(), name='me'),
]
