"""
Management command to create test users for each role
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for each role'
    
    def handle(self, *args, **options):
        roles = [
            ('ADMIN', 'admin@example.com', 'Admin User'),
            ('FM', 'fm@example.com', 'FM User'),
            ('CONTRACTOR', 'contractor@example.com', 'Contractor User'),
            ('CUSTOMER', 'customer@example.com', 'Customer User'),
            ('INVESTOR', 'investor@example.com', 'Investor User'),
        ]
        
        for role, email, username in roles:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password='Test@123',
                    role=role,
                    is_verified=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created {role} user: {email}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'{role} user already exists: {email}')
                )
        
        # Create superuser if doesn't exist
        if not User.objects.filter(email='superadmin@example.com').exists():
            User.objects.create_superuser(
                email='superadmin@example.com',
                username='Super Admin',
                password='Admin@123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: superadmin@example.com')
            )
