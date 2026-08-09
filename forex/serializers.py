from rest_framework import serializers
from .models import User, Deposit
from django.conf import settings


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    staff_secret_key = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'telegram_username', 'country', 'service', 'password', 'staff_secret_key')

    def create(self, validated_data):
        provided_key = validated_data.pop('staff_secret_key', None)
        is_staff = False
        role = 'USER'

        # Check if provided secret key matches settings.STAFF_SECRET_KEY
        if provided_key and provided_key == getattr(settings, 'STAFF_SECRET_KEY', None):
            is_staff = True
            role = 'ADMIN'

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            telegram_username=validated_data.get('telegram_username', ''),
            country=validated_data.get('country', ''),
            service=validated_data.get('service', ''),
            is_staff=is_staff,
            role=role
        )
        return user

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ('id', 'reference', 'coin', 'amount', 'status', 'created_at')
        read_only_fields = ('id', 'reference', 'status', 'created_at')


class UserDashboardSerializer(serializers.ModelSerializer):
    deposits = DepositSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'full_name', 'email', 'telegram_username', 
            'country', 'service', 'status', 'balance', 'role', 'deposits','is_staff', 'date_joined',
        )


class AdminUserManagementSerializer(serializers.ModelSerializer):
    total_deposits = serializers.IntegerField(source='deposits.count', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'full_name', 'email', 'telegram_username', 
            'country', 'service', 'status', 'balance', 'role',
            'is_staff', 'date_joined', 'total_deposits'
        )


class AdminDepositManagementSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.full_name')

    class Meta:
        model = Deposit
        fields = (
            'id', 'reference', 'user', 'user_email', 
            'user_name', 'coin', 'amount', 'status', 'created_at'
        )
        read_only_fields = ('id', 'reference', 'user', 'created_at')