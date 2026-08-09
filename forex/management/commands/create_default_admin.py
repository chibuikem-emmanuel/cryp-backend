import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates or updates the default admin superuser account'

    def handle(self, *args, **options):
        # Define default credentials (or pull from .env)
        email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@platform.com')
        password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'AdminSecure26!')
        full_name = 'System Administrator'

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        # Set/reset password and explicitly grant admin attributes
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        
        # Ensure custom fields match your API requirements
        if hasattr(user, 'status'):
            user.status = 'APPROVED'
        if hasattr(user, 'role'):
            user.role = 'ADMIN'

        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created default admin: {email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated credentials for existing admin: {email}'))