from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserTransactionListView(generics.ListAPIView):
    """
    GET /api/me/transactions/
    List current user's transactions with pagination.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TransactionPagination

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
