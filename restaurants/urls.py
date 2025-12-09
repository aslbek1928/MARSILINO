from django.urls import path
from .views import (
    RestaurantListView, 
    RestaurantDetailView,
    CashierLoginView,
    CashierCreateView,
    CashierPINResetView
)

urlpatterns = [
    # Public restaurant endpoints
    path('', RestaurantListView.as_view(), name='restaurant-list'),
    path('<uuid:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    
    # Cashier auth
    path('cashier/auth/login/', CashierLoginView.as_view(), name='cashier-login'),
]

# Admin-only cashier management (will be included under /api/restaurant-admin/)
cashier_admin_patterns = [
    path('cashiers/', CashierCreateView.as_view(), name='cashier-create'),
    path('cashiers/reset-pin/', CashierPINResetView.as_view(), name='cashier-reset-pin'),
]

