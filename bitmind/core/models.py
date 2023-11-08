"""
This is where the models of the application are defined
"""
from decimal import Decimal

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Cryptocurrency(models.Model):
    """Each crypto coin will be one entry"""

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Transaction of a specific coin from a specific user"""

    TYPE_CHOICES = (
        ("buy", "Buy"),
        ("sell", "Sell"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    date = models.DateTimeField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=30, decimal_places=5, validators=[MinValueValidator(Decimal("0.01"))]
    )
    price = models.DecimalField(
        max_digits=20, decimal_places=5, validators=[MinValueValidator(Decimal("0.01"))]
    )

    def __str__(self):
        return f"{self.user.email}: {'bought' if self.type =='buy' else 'sold'} '{self.amount} {self.crypto.symbol}' at the price of '${self.price}'"


class UserCoin(models.Model):
    """Coins owned of a coin X from a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=5)

    def __str__(self):
        return f"{self.user.email} - {self.crypto.symbol}: {self.amount}"

    class Meta:
        unique_together = ("user", "crypto")
