import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email address is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('status', 'APPROVED')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, default='USER')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Deposit(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    reference = models.CharField(max_length=20, unique=True, editable=False)
    coin = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.reference = f"DEP-{code}"

        if self.pk:
            previous_status = Deposit.objects.filter(pk=self.pk).values_list('status', flat=True).first()
            if previous_status != 'APPROVED' and self.status == 'APPROVED':
                self.user.balance += self.amount
                self.user.status = 'APPROVED'
                self.user.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.coin} {self.amount} ({self.status})"