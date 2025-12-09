from django.urls import path
from .views import UserTransactionListView

urlpatterns = [
    path('', UserTransactionListView.as_view(), name='user-transactions'),
]
