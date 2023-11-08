from django.utils import timezone
from rest_framework import serializers

from core.models import Cryptocurrency  # Cryptocurrency only altered by admin
from core.models import Transaction  # Can be altered by user
from core.models import UserCoin  # Only altered by Transaction


class CryptocurrencySerializer(serializers.ModelSerializer):
    """Serializer for Cryptocurrency."""

    class Meta:
        model = Cryptocurrency
        fields = ["symbol", "name"]
        read_only_fields = ["symbol", "name"]


class UserCoinSerializer(serializers.ModelSerializer):
    """Serializer for User Coin holdings."""

    class Meta:
        model = UserCoin
        fields = ["id", "crypto", "amount"]
        read_only_fields = ["id", "crypto", "amount"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "crypto", "date", "type", "amount", "price"]
        read_only_fields = ["id"]

    def validate_crypto(self, value):
        # Check if the specified crypto exists in the database
        try:
            Cryptocurrency.objects.get(pk=value.pk)
        except Cryptocurrency.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid crypto. This crypto does not exist."
            )
        return value

    def validate_date(self, value):
        # Check if the date is in the future
        if value > timezone.now():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value

    def validate_type(self, value):
        # Check if the transaction type is one of the specified choices
        if value not in dict(Transaction.TYPE_CHOICES):
            raise serializers.ValidationError("Invalid transaction type.")
        return value

    def validate_amount(self, value):
        # Check if the amount is negative
        if value < 0:
            raise serializers.ValidationError("Amount cannot be negative.")
        return value

    def validate_price(self, value):
        # Check if the amount is negative
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
