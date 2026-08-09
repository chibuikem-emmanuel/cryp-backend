from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Sum

from .models import User, Deposit
from .permissions import IsAdminUserRole
from .serializers import (
    UserRegisterSerializer, 
    DepositSerializer, 
    UserDashboardSerializer,
    AdminUserManagementSerializer,
    AdminDepositManagementSerializer
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserDashboardSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        raw_email = request.data.get('email', '')
        email = raw_email.strip().lower() if isinstance(raw_email, str) else ''
        password = request.data.get('password', '')

        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if user is None:
            try:
                found_user = User.objects.get(email__iexact=email)
                if found_user.check_password(password):
                    user = found_user
            except User.DoesNotExist:
                user = None

        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'User account is disabled'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserDashboardSerializer(user).data
        }, status=status.HTTP_200_OK)


class UserDepositView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            deposit = serializer.save(user=request.user)
            return Response(DepositSerializer(deposit).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDashboardSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminOverviewView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        total_users = User.objects.filter(is_staff=False).count()
        pending_deposits = Deposit.objects.filter(status='PENDING').count()
        total_approved_amount = Deposit.objects.filter(status='APPROVED').aggregate(
            total=Sum('amount')
        )['total'] or 0.00
        total_user_balance = User.objects.filter(is_staff=False).aggregate(
            total=Sum('balance')
        )['total'] or 0.00

        return Response({
            'total_users': total_users,
            'pending_deposits_count': pending_deposits,
            'total_deposited_amount': float(total_approved_amount),
            'total_user_balance': float(total_user_balance),
        })


class AdminDepositsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        status_filter = request.query_params.get('status')
        deposits = Deposit.objects.select_related('user').all().order_by('-created_at')
        
        if status_filter:
            deposits = deposits.filter(status=status_filter.upper())
            
        serializer = AdminDepositManagementSerializer(deposits, many=True)
        return Response(serializer.data)


class AdminDepositDetailView(APIView):
    permission_classes = [IsAdminUserRole]

    def delete(self, request, pk):
        try:
            deposit = Deposit.objects.get(pk=pk)
            deposit.delete()
            return Response({'message': 'Deposit record deleted successfully.'}, status=status.HTTP_200_OK)
        except Deposit.DoesNotExist:
            return Response({'error': 'Deposit record not found.'}, status=status.HTTP_404_NOT_FOUND)


class AdminDepositActionView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request, pk):
        action = request.data.get('action', '').upper()
        if action not in ['APPROVE', 'REJECT']:
            return Response({'error': 'Action must be APPROVE or REJECT'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            deposit = Deposit.objects.get(pk=pk)
        except Deposit.DoesNotExist:
            return Response({'error': 'Deposit not found'}, status=status.HTTP_404_NOT_FOUND)

        deposit.status = 'APPROVED' if action == 'APPROVE' else 'REJECTED'
        deposit.save()

        return Response(AdminDepositManagementSerializer(deposit).data, status=status.HTTP_200_OK)


class AdminUsersView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        users = User.objects.filter(is_staff=False).order_by('-date_joined')
        serializer = AdminUserManagementSerializer(users, many=True)
        return Response(serializer.data)


class AdminUserUpdateView(APIView):
    permission_classes = [IsAdminUserRole]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'balance' in request.data:
            user.balance = request.data['balance']
        if 'status' in request.data:
            user.status = request.data['status']

        user.save()
        return Response(AdminUserManagementSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Protect against self-deletion if an admin triggers it on their account
        if request.user.id == user.id:
            return Response({'error': 'You cannot delete your own active admin account.'}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_200_OK)