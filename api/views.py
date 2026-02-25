from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import translation
from .models import Tag, Restaurant
from .serializers import TagSerializer, RestaurantSerializer

class UserLanguageMixin:
    """Activates the user's preferred language if authenticated."""
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.user.is_authenticated:
            # The language field corresponds to our supported language codes (en, ru, uz)
            translation.activate(request.user.language)
            request.LANGUAGE_CODE = translation.get_language()

class TagListView(UserLanguageMixin, generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class RestaurantListView(UserLanguageMixin, generics.ListAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Restaurant.objects.all()
        tags_param = self.request.query_params.get('tags')
        if tags_param:
            tag_ids = [t.strip() for t in tags_param.split(',')]
            for tag_id in tag_ids:
                queryset = queryset.filter(tags__id=tag_id)
        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

import uuid
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import RedeemedReceipt, WalletTransaction, CustomUser
from .services import verify_soliq_receipt, SoliqVerificationError

class WalletView(UserLanguageMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        transactions = WalletTransaction.objects.filter(user=user, status='completed')
        total_earned = sum(t.amount for t in transactions if t.type == 'cashback_add')
        total_transferred = sum(t.amount for t in transactions if t.type == 'transfer_out')

        return Response({
            "success": True,
            "data": {
                "user_id": str(user.id) if hasattr(user, 'id') else user.phone_number,
                "balance": float(user.wallet_balance),
                "currency": "UZS",
                "total_earned": float(total_earned),
                "total_transferred": float(total_transferred),
                "last_updated": timezone.now().isoformat()
            }
        })

class WalletAddView(UserLanguageMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        receipt_id = data.get('receipt_id')
        total_paid = float(data.get('total_paid', 0))
        cashback_percentage = float(data.get('cashback_percentage', 0))
        cashback_amount = float(data.get('cashback_amount', 0))
        restaurant_id = data.get('restaurant_id')

        if RedeemedReceipt.objects.filter(receipt_id=receipt_id).exists():
            return Response({
                "success": False,
                "error": "RECEIPT_ALREADY_REDEEMED",
                "message": "This receipt has already been used for cashback."
            }, status=409)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({
                "success": False,
                "error": "RESTAURANT_NOT_FOUND",
                "message": "Restaurant not found."
            }, status=422)

        with transaction.atomic():
            user = CustomUser.objects.select_for_update().get(id=request.user.id)
            RedeemedReceipt.objects.create(
                receipt_id=receipt_id,
                receipt_number=receipt_id.split('_')[-1] if '_' in receipt_id else receipt_id,
                user=user,
                restaurant=restaurant,
                total_paid=total_paid,
                cashback_amount=cashback_amount
            )

            balance_before = user.wallet_balance
            balance_after = float(balance_before) + cashback_amount
            user.wallet_balance = balance_after
            user.save()

            txn_id = f"txn_{uuid.uuid4().hex[:10]}"
            WalletTransaction.objects.create(
                transaction_id=txn_id,
                user=user,
                type='cashback_add',
                amount=cashback_amount,
                balance_before=balance_before,
                balance_after=balance_after,
                receipt_id=receipt_id,
                restaurant_id=restaurant_id
            )

        return Response({
            "success": True,
            "data": {
                "transaction_id": txn_id,
                "new_balance": float(balance_after),
                "cashback_amount": float(cashback_amount),
                "receipt_id": receipt_id
            }
        })

class WalletTransferView(UserLanguageMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = float(request.data.get('amount', 0))
        card_last_four = request.data.get('card_last_four')

        with transaction.atomic():
            user = CustomUser.objects.select_for_update().get(id=request.user.id)
            balance_before = float(user.wallet_balance)

            if balance_before < amount or amount <= 0:
                return Response({
                    "success": False,
                    "error": "INSUFFICIENT_BALANCE",
                    "message": "Not enough balance to transfer."
                }, status=400)

            balance_after = balance_before - amount
            user.wallet_balance = balance_after
            user.save()

            txn_id = f"txn_{uuid.uuid4().hex[:10]}"
            WalletTransaction.objects.create(
                transaction_id=txn_id,
                user=user,
                type='transfer_out',
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                card_last_four=card_last_four
            )

        return Response({
            "success": True,
            "data": {
                "transaction_id": txn_id,
                "transferred_amount": amount,
                "new_balance": float(balance_after),
                "card_last_four": card_last_four,
                "estimated_arrival": (timezone.now() + timezone.timedelta(days=1)).isoformat()
            }
        })

class ReceiptVerifyView(UserLanguageMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qr_code = request.data.get('qr_code_url') or request.data.get('qr_code')
        req_restaurant_id = request.data.get('restaurant_id')

        if not qr_code:
            return Response({"success": False, "error": "MISSING_DATA", "message": "qr_code is required"}, status=400)

        try:
            parsed_data = verify_soliq_receipt(qr_code)
        except SoliqVerificationError as e:
            return Response({"success": False, "error": "INVALID_FORMAT", "message": str(e)}, status=400)

        receipt_id = parsed_data['receipt_id']
        tin = parsed_data['tin']
        total_amount = parsed_data['total_amount']

        try:
            restaurant = Restaurant.objects.get(tin=tin)
        except Restaurant.DoesNotExist:
            return Response({
                "success": False,
                "error": "RESTAURANT_MISMATCH",
                "message": "This receipt does not belong to any registered restaurant."
            }, status=422)

        if req_restaurant_id and str(restaurant.id) != str(req_restaurant_id):
            return Response({
                "success": False,
                "error": "RESTAURANT_MISMATCH",
                "message": "This receipt does not belong to the requesting restaurant."
            }, status=422)

        already_redeemed = RedeemedReceipt.objects.filter(receipt_id=receipt_id).exists()

        if already_redeemed:
            return Response({
                "success": False,
                "error": "RECEIPT_ALREADY_REDEEMED",
                "message": "This receipt has already been redeemed."
            }, status=409)

        cashback_earned = (float(total_amount) * float(restaurant.cashback_percentage)) / 100.0

        with transaction.atomic():
            user = CustomUser.objects.select_for_update().get(id=request.user.id)
            
            RedeemedReceipt.objects.create(
                receipt_id=receipt_id,
                receipt_number=parsed_data['receipt_number'],
                user=user,
                restaurant=restaurant,
                total_paid=total_amount,
                cashback_amount=cashback_earned
            )

            balance_before = user.wallet_balance
            balance_after = float(balance_before) + cashback_earned
            user.wallet_balance = balance_after
            user.save()

            txn_id = f"txn_{uuid.uuid4().hex[:10]}"
            WalletTransaction.objects.create(
                transaction_id=txn_id,
                user=user,
                type='cashback_add',
                amount=cashback_earned,
                balance_before=balance_before,
                balance_after=balance_after,
                receipt_id=receipt_id,
                restaurant_id=restaurant.id
            )

        return Response({
            "success": True,
            "data": {
                "receipt_id": receipt_id,
                "receipt_number": parsed_data['receipt_number'],
                "total_amount": float(total_amount),
                "restaurant_name": restaurant.name,
                "created_at": parsed_data['created_at'],
                "tin": tin,
                "already_redeemed": False,
                # Additional fields expected by frontend
                "total_paid": float(total_amount),
                "cashback_earned": float(cashback_earned),
                "new_wallet_balance": float(balance_after),
            }
        })

from .serializers import UserProfileSerializer

class MeView(UserLanguageMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({
            "success": True,
            "data": serializer.data
        })

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "data": serializer.data
            })
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=400)
