"""
Management command to unlock locked accounts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from authentication.models import User


class Command(BaseCommand):
    help = 'Unlock accounts that have passed their lock duration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Unlock specific user by email',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Unlock all locked accounts',
        )
    
    def handle(self, *args, **options):
        email = options.get('email')
        unlock_all = options.get('all')
        
        if email:
            try:
                user = User.objects.get(email=email)
                if user.is_account_locked:
                    user.unlock_account()
                    self.stdout.write(
                        self.style.SUCCESS(f'Unlocked account: {email}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Account is not locked: {email}')
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User not found: {email}')
                )
        
        elif unlock_all:
            locked_users = User.objects.filter(
                account_locked_until__isnull=False
            )
            count = 0
            for user in locked_users:
                user.unlock_account()
                count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Unlocked {count} accounts')
            )
        
        else:
            # Unlock accounts that have passed their lock duration
            now = timezone.now()
            expired_locks = User.objects.filter(
                account_locked_until__lt=now
            )
            count = 0
            for user in expired_locks:
                user.unlock_account()
                count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Unlocked {count} accounts with expired locks')
            )
