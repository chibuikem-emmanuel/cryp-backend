from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    UserDepositView, 
    UserDashboardView,
    AdminOverviewView,
    AdminDepositsView,
    AdminDepositDetailView,
    AdminDepositActionView,
    AdminUsersView,
    AdminUserUpdateView,
)

urlpatterns = [
    # User Endpoints
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('user/me/', UserDashboardView.as_view(), name='user-me'),
    path('user/dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('user/deposit/', UserDepositView.as_view(), name='user-deposit'),

    # Admin Endpoints
    path('admin/overview/', AdminOverviewView.as_view(), name='admin-overview'),
    path('admin/deposits/', AdminDepositsView.as_view(), name='admin-deposits'),
    path('admin/deposits/<int:pk>/', AdminDepositDetailView.as_view(), name='admin-deposit-detail'),
    path('admin/deposits/<int:pk>/action/', AdminDepositActionView.as_view(), name='admin-deposit-action'),
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', AdminUserUpdateView.as_view(), name='admin-user-update'),
]