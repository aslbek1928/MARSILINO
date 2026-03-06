from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.utils import translation, timezone
from django.db import transaction
import uuid, math
from rest_framework_simplejwt.tokens import RefreshToken
import random
from .models import Tag, Restaurant, RedeemedReceipt, WalletTransaction, CustomUser, FCMDevice, OTP
from .serializers import (
    TagSerializer, RestaurantSerializer, WalletTransactionSerializer, 
    FCMDeviceSerializer, RegisterSerializer, UserProfileSerializer,
    OTPSendSerializer, OTPVerifySerializer, ReviewSerializer
)
from rest_framework.pagination import PageNumberPagination

import math

class UserLanguageMixin:
    """Activates the user's preferred language if authenticated."""
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.user.is_authenticated:
            # The language field corresponds to our supported language codes (en, ru, uz)
            translation.activate(request.user.language)
            request.LANGUAGE_CODE = translation.get_language()

class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    
    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "data": data,
            "total": self.page.paginator.count,
            "page": self.page.number,
            "pages": self.page.paginator.num_pages
        })

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
        # Add filtering by liked status if requested or pass it in serializer context
        tags_param = self.request.query_params.get('tags')
        if tags_param:
            tag_ids = [t.strip() for t in tags_param.split(',')]
            for tag_id in tag_ids:
                queryset = queryset.filter(tags__id=tag_id)
        
        # Add filtering by specific restaurant ID
        restaurant_id = self.request.query_params.get('id') or self.request.query_params.get('restaurant_id')
        if restaurant_id:
            queryset = queryset.filter(id=restaurant_id)
            
        return queryset.distinct().order_by('name')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

from .services import verify_soliq_receipt, SoliqVerificationError

class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "ok", "message": "Backend is running"}, status=200)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "User registered successfully",
                "data": {
                    "phone_number": user.phone_number,
                    "full_name": user.full_name
                }
            }, status=201)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=400)

class OTPSendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user = CustomUser.objects.filter(phone_number=phone_number).first()
            OTP.objects.create(phone_number=phone_number, code=code, user=user)
            return Response({
                "success": True,
                "message": "OTP sent successfully",
                "otp_code": code
            })
        return Response({"success": False, "errors": serializer.errors}, status=400)

class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            full_name = serializer.validated_data.get('full_name', '')
            otp = OTP.objects.filter(phone_number=phone_number, code=code, is_verified=False).first()
            if otp:
                otp.is_verified = True
                otp.save()
                user, created = CustomUser.objects.get_or_create(phone_number=phone_number, defaults={'full_name': full_name})
                if not created and full_name:
                    user.full_name = full_name
                    user.save()
                
                # Link the OTP to the user if it wasn't linked before
                if not otp.user:
                    otp.user = user
                    otp.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "success": True,
                    "is_new_user": created,
                    "tokens": {"refresh": str(refresh), "access": str(refresh.access_token)},
                    "user": {"phone_number": user.phone_number, "full_name": user.full_name, "wallet_balance": float(user.wallet_balance)}
                })
            return Response({"success": False, "error_code": "INVALID_OTP", "message": "Incorrect or expired code."}, status=401)
        return Response({"success": False, "errors": serializer.errors}, status=400)

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

class WalletTransactionListView(UserLanguageMixin, generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return WalletTransaction.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
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
                "error_code": "RECEIPT_ALREADY_REDEEMED",
                "message": "This receipt has already been used for cashback."
            }, status=409)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({
                "success": False,
                "error_code": "RESTAURANT_NOT_FOUND",
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
                    "error_code": "INSUFFICIENT_BALANCE",
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
            return Response({"success": False, "error_code": "MISSING_DATA", "message": "qr_code is required"}, status=400)

        try:
            parsed_data = verify_soliq_receipt(qr_code)
        except SoliqVerificationError as e:
            return Response({"success": False, "error_code": "INVALID_FORMAT", "message": str(e)}, status=400)

        # Extract data from the parsed QR code receipt
        receipt_id = parsed_data['receipt_id']
        tin = parsed_data['tin']
        total_amount = parsed_data['total_amount']

        # If the mobile app provides the restaurant ID they are attempting to scan for,
        # we strictly match the TIN of that specific restaurant against the TIN on the receipt
        if req_restaurant_id:
            try:
                restaurant = Restaurant.objects.get(id=req_restaurant_id)
            except Restaurant.DoesNotExist:
                return Response({
                    "success": False,
                    "error_code": "RESTAURANT_NOT_FOUND",
                    "message": "The requesting restaurant could not be found."
                }, status=404)

            # Compare the exact TIN from the QR to the known TIN of the requested restaurant
            if str(restaurant.tin) != str(tin):
                return Response({
                    "success": False,
                    "error_code": "RESTAURANT_MISMATCH",
                    "message": "This receipt's tax identification number (TIN) does not match the chosen restaurant."
                }, status=422)
                
        else:
            # Fallback if the mobile app didn't send a specific restaurant ID,
            # we try to see if ANY registered restaurant matches this TIN.
            try:
                restaurant = Restaurant.objects.get(tin=tin)
            except Restaurant.DoesNotExist:
                return Response({
                    "success": False,
                    "error_code": "RESTAURANT_MISMATCH",
                    "message": "This receipt does not belong to any registered restaurant."
                }, status=422)

        already_redeemed = RedeemedReceipt.objects.filter(receipt_id=receipt_id).exists()

        if already_redeemed:
            return Response({
                "success": False,
                "error_code": "RECEIPT_ALREADY_REDEEMED",
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
                "total_paid": float(total_amount),
                "cashback_earned": float(cashback_earned),
                "new_wallet_balance": float(balance_after),
            }
        })


class ReceiptScrapeView(UserLanguageMixin, APIView):
    """
    A standalone endpoint specifically for scraping data from a Soliq QR code URL.
    This doesn't verify or add cashback, it just returns the scraped data.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qr_code = request.data.get('qr_code_url')
        
        if not qr_code:
            return Response({
                "success": False, 
                "error_code": "MISSING_DATA", 
                "message": "qr_code_url is required"
            }, status=400)

        try:
            parsed_data = verify_soliq_receipt(qr_code)
            return Response({
                "success": True,
                "data": {
                    "tin": parsed_data['tin'],
                    "total_amount": float(parsed_data['total_amount']),
                    "receipt_id": parsed_data['receipt_id'],
                    "created_at": parsed_data['created_at']
                }
            })
        except SoliqVerificationError as e:
            return Response({
                "success": False, 
                "error_code": "SCRAPE_FAILED", 
                "message": str(e)
            }, status=422)


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

class UserCardUpdateView(UserLanguageMixin, APIView):
    """
    Allows updating a user's 16-digit card number via a GET request.
    Example: GET /api/v1/me/card/add/?phone_number=+998901234567&card_number=8600123456789012
    """
    permission_classes = [AllowAny]

    def get(self, request):
        phone_number = request.query_params.get('phone_number')
        card_number = request.query_params.get('card_number')
        
        if not phone_number or not card_number:
            return Response({
                "success": False,
                "error_code": "MISSING_PARAMETERS",
                "message": "Both phone_number and card_number query parameters are required."
            }, status=400)

        # Ensure phone number has '+' prefix if missing but provided as a query param
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number.lstrip(' ')

        from .models import CustomUser
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "error_code": "USER_NOT_FOUND",
                "message": f"User with phone number {phone_number} not found."
            }, status=404)

        user.card_number = card_number
        try:
            user.full_clean(exclude=['password'])
            user.save()
            return Response({
                "success": True,
                "message": "Card number updated successfully.",
                "data": {
                    "phone_number": user.phone_number,
                    "card_number": user.card_number
                }
            })
        except Exception as e:
            return Response({
                "success": False,
                "error_code": "INVALID_CARD_NUMBER",
                "message": str(e)
            }, status=400)

class LikedRestaurantListView(UserLanguageMixin, generics.ListAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.liked_restaurants.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class LikedRestaurantView(UserLanguageMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, restaurant_id, action):
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({
                "success": False, 
                "error_code": "RESTAURANT_NOT_FOUND", 
                "message": "Restaurant not found."
            }, status=404)

        if action == 'add':
            request.user.liked_restaurants.add(restaurant)
        elif action == 'remove':
            request.user.liked_restaurants.remove(restaurant)
        else:
            return Response({
                "success": False, 
                "error_code": "INVALID_ACTION", 
                "message": "Action must be 'add' or 'remove'."
            }, status=400)

        return Response({
            "success": True,
            "message": f"Restaurant {action}ed successfully."
        })

class FCMDeviceView(UserLanguageMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FCMDeviceSerializer(data=request.data)
        if serializer.is_valid():
            fcm_token = serializer.validated_data['fcm_token']
            device_type = serializer.validated_data['device_type']
            
            # Update or create device registration
            FCMDevice.objects.update_or_create(
                fcm_token=fcm_token,
                defaults={'user': request.user, 'device_type': device_type}
            )
            
            return Response({
                "success": True,
                "message": "Device registered successfully."
            })
        return Response({
            "success": False,
            "error_code": "INVALID_DATA",
            "errors": serializer.errors
        }, status=400)


class RestaurantRateView(UserLanguageMixin, APIView):
    """
    Allows an authenticated user to rate a restaurant from 1 to 5.
    If the user has already rated the restaurant, their existing rating is updated.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, restaurant_id):
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({
                "success": False, 
                "error_code": "RESTAURANT_NOT_FOUND", 
                "message": "Restaurant not found."
            }, status=404)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            
            # Update or create the review for this specific user and restaurant
            from .models import Review
            review, created = Review.objects.update_or_create(
                user=request.user,
                restaurant=restaurant,
                defaults={'rating': rating}
            )
            
            return Response({
                "success": True,
                "message": f"Successfully {'added' if created else 'updated'} rating for {restaurant.name}.",
                "data": {
                    "restaurant_id": restaurant.id,
                    "new_rating": rating,
                    "average_rating": restaurant.average_rating,
                    "total_reviews": restaurant.total_reviews
                }
            })
            
        return Response({
            "success": False,
            "error_code": "INVALID_RATING",
            "errors": serializer.errors
        }, status=400)
