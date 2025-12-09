from django.urls import path
from .rap_views import (
    RestaurantUsersView,
    RestaurantUsersExportView,
    CashierListCreateView,
    CashierDetailView,
    CashierRegeneratePINView,
    RestaurantSettingsView,
    RestaurantGalleryUploadView
)

# All these endpoints are under /api/restaurant-admin/
urlpatterns = [
    # Users overview
    path('users/', RestaurantUsersView.as_view(), name='rap-users'),
    path('users/export/', RestaurantUsersExportView.as_view(), name='rap-users-export'),
    
    # Cashier management
    path('cashiers/', CashierListCreateView.as_view(), name='rap-cashiers'),
    path('cashiers/<uuid:cashier_id>/', CashierDetailView.as_view(), name='rap-cashier-detail'),
    path('cashiers/<uuid:cashier_id>/regenerate-pin/', CashierRegeneratePINView.as_view(), name='rap-cashier-regenerate-pin'),
    
    # Restaurant settings
    path('restaurant/', RestaurantSettingsView.as_view(), name='rap-restaurant'),
    path('restaurant/gallery/', RestaurantGalleryUploadView.as_view(), name='rap-gallery-upload'),
]
