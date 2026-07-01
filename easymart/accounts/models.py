from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


# ======================================================
# CUSTOM USER MODEL
# ======================================================

class User(AbstractUser):
    """
    Custom User Model
    """

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.username


# ======================================================
# OTP MODEL
# ======================================================

class OTPCode(models.Model):

    PURPOSE_SIGNUP = 'signup'
    PURPOSE_LOGIN = 'login'
    PURPOSE_RESET = 'reset'

    PURPOSE_CHOICES = [
        (PURPOSE_SIGNUP, 'Signup'),
        (PURPOSE_LOGIN, 'Login'),
        (PURPOSE_RESET, 'Password Reset'),
    ]

    email = models.EmailField(
        blank=True,
        null=True,
        db_index=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    code = models.CharField(
        max_length=6
    )

    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES
    )

    verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        """
        OTP valid for 5 minutes
        """
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        contact = self.email if self.email else self.phone
        return f"{contact} - {self.code}"


# ======================================================
# ADDRESS MODEL
# ======================================================

class Address(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    full_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    address_line = models.TextField()

    city = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):

        # First address automatically becomes default
        if not Address.objects.filter(user=self.user).exists():
            self.is_default = True

        # Ensure only one default address exists
        if self.is_default:
            Address.objects.filter(
                user=self.user
            ).exclude(
                id=self.pk
            ).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city}"