from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Deposit


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'telegram_username', 'service', 'role', 'status', 'balance', 'is_staff')
    list_filter = ('status', 'role', 'service', 'is_staff', 'date_joined')
    search_fields = ('email', 'full_name', 'telegram_username')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'telegram_username', 'country', 'service')}),
        ('Account Status & Role', {'fields': ('role', 'status', 'balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('date_joined',)}),
    )
    readonly_fields = ('date_joined',)


@admin.action(description="Approve selected deposits...")
def approve_deposits(modeladmin, request, queryset):
    for deposit in queryset.filter(status='PENDING'):
        deposit.status = 'APPROVED'
        deposit.save()


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'coin', 'amount', 'status', 'created_at')
    list_filter = ('status', 'coin', 'created_at')
    search_fields = ('reference', 'user__email', 'user__full_name')
    actions = [approve_deposits]





