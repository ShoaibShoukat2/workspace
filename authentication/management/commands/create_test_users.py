from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users for development'

    def handle(self, *args, **options):
        test_users = [
            {
                'email': 'admin@apex.com',
                'username': 'admin',
                'password': 'admin123',
                'role': 'admin',
                'is_verified': True
            },
            {
                'email': 'fm@apex.com',
                'username': 'fieldmanager',
                'password': 'fm123',
                'role': 'fm',
                'is_verified': True
            },
            {
                'email': 'contractor@apex.com',
                'username': 'contractor',
                'password': 'contractor123',
                'role': 'contractor',
                'is_verified': True
            },
            {
                'email': 'investor@apex.com',
                'username': 'investor',
                'password': 'investor123',
                'role': 'investor',
                'is_verified': True
            },
            {
                'email': 'customer@apex.com',
                'username': 'customer',
                'password': 'customer123',
                'role': 'customer',
                'is_verified': True
            }
        ]

        for user_data in test_users:
            email = user_data['email']
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {email} already exists')
                )
                continue

            user = User.objects.create_user(
                email=email,
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                is_verified=user_data['is_verified']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created user: {email} (role: {user.role})')
            )

        self.stdout.write(
            self.style.SUCCESS('\nTest users created successfully!')
        )
        self.stdout.write('You can now login with:')
        for user_data in test_users:
            self.stdout.write(f'  Email: {user_data["email"]} | Password: {user_data["password"]} | Role: {user_data["role"]}')