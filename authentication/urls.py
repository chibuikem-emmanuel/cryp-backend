from django.urls import path
from .views import RegisterAdminView, AdminLoginView

urlpatterns = [
    path('register-staff/', RegisterAdminView.as_view(), name='register-staff'),
    path('login/', AdminLoginView.as_view(), name='admin-login'),
]