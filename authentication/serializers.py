from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
ADMIN_BOOTSTRAP_SECRET = "ADMIN_12345"

class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    secret_key = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'telegram_username', 'password', 'secret_key']

    def validate_secret_key(self, value):
        if value != ADMIN_BOOTSTRAP_SECRET:
            raise serializers.ValidationError("Invalid admin registration secret key.")
        return value

    def create(self, validated_data):
        validated_data.pop('secret_key')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            is_staff=True,
            is_superuser=True,
            role='ADMIN',
            status='APPROVED',
            **validated_data
        )
        return user

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_staff and user.role != 'ADMIN':
            raise serializers.ValidationError("Access denied. Admin privileges required.")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_staff': user.is_staff
            }
        }