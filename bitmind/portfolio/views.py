from core.models import Cryptocurrency, Transaction, UserCoin
from core.permissions import ReadOnlyOrAdminOnly
from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from portfolio.pagination import StandardResultsSetPagination
from portfolio.serializers import (
    CryptocurrencySerializer,
    TransactionSerializer,
    UserCoinSerializer,
)
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

mixins.ListModelMixin


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        with db_transaction.atomic():
            transaction = serializer.save(user=self.request.user)
            self.update_user_coin(transaction)
            if self.check_negative_holdings(transaction):
                raise serializers.ValidationError(
                    "Transaction would result in negative holdings."
                )

    def perform_update(self, serializer):
        with db_transaction.atomic():
            transaction = serializer.save(user=self.request.user)
            self.update_user_coin(transaction)
            if self.check_negative_holdings(transaction):
                raise serializers.ValidationError(
                    "Transaction would result in negative holdings."
                )

    def perform_destroy(self, instance):
        with db_transaction.atomic():
            instance.delete()
            self.update_user_coin(instance)
            if self.check_negative_holdings(instance):
                raise serializers.ValidationError(
                    "Deleting this 'buy' transaction would result in negative holdings."
                )

    def update_user_coin(self, transaction):
        user = self.request.user
        crypto = transaction.crypto
        total_amount = self.calculate_user_crypto_total(transaction)

        if total_amount == 0:
            UserCoin.objects.filter(user=user, crypto=crypto).delete()
        else:
            user_coin, _ = UserCoin.objects.get_or_create(
                user=user,
                crypto=crypto,
                defaults={"amount": total_amount},
            )
            user_coin.amount = total_amount
            user_coin.save()

    def check_negative_holdings(self, transaction):
        return self.calculate_user_crypto_total(transaction) < 0

    def calculate_user_crypto_total(self, transaction):
        user = self.request.user
        crypto = transaction.crypto
        total_bought = (
            Transaction.objects.filter(user=user, crypto=crypto, type="buy")
            .aggregate(Sum("amount"))
            .get("amount__sum")
            or 0
        )
        total_sold = (
            Transaction.objects.filter(user=user, crypto=crypto, type="sell")
            .aggregate(Sum("amount"))
            .get("amount__sum")
            or 0
        )
        return total_bought - total_sold

    def get_queryset(self):
        # Retrieve all UserCoin objects for the authenticated user
        return self.queryset.filter(user=self.request.user).order_by("-date")


class UserHoldingsViewSet(viewsets.ReadOnlyModelViewSet):
    """View that returns all the user's Coin holdings"""

    queryset = Transaction.objects.all()
    serializer_class = UserCoinSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve all UserCoin objects for the authenticated user
        return self.queryset.filter(user=self.request.user).order_by("-amount")


class CryptocurrencyViewSet(viewsets.ModelViewSet):
    queryset = Cryptocurrency.objects.all()
    serializer_class = CryptocurrencySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [ReadOnlyOrAdminOnly]

    # Set pagination class and page size within the view class
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        contains = self.request.query_params.get("query", None)

        # Filter the queryset based on the "query" parameter
        if contains:
            queryset = Cryptocurrency.objects.filter(Q(name__icontains=contains))
        else:
            queryset = Cryptocurrency.objects.all()

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query",
                type=OpenApiTypes.STR,
                description="String to filter cryptocurrencies by name (First 10)",
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
