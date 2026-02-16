from django.urls import path
from .views import (
    RestaurantListView, 
    RestaurantDetailView,
    CashierLoginView,
    CashierCreateView,
    CashierPINResetView,
    CashierCreateView,
    CashierPINResetView,
    BookTableAPIView,
    rap_page_view,
    update_booking_status,
)

urlpatterns = [
    # Public restaurant endpoints
    path('rap/', rap_page_view, name='rap_page'),
    path('rap/update-booking-status/', update_booking_status, name='update-booking-status'),
    path('', RestaurantListView.as_view(), name='restaurant-list'),
    path('<uuid:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('book-table/', BookTableAPIView.as_view(), name='book-table'),
    
    # Cashier auth
    path('cashier/auth/login/', CashierLoginView.as_view(), name='cashier-login'),
]

# Admin-only cashier management (will be included under /api/restaurant-admin/)
cashier_admin_patterns = [
    path('cashiers/', CashierCreateView.as_view(), name='cashier-create'),
    path('cashiers/reset-pin/', CashierPINResetView.as_view(), name='cashier-reset-pin'),
]

