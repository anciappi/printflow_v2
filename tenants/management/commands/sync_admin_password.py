"""
Management command to sync the admin password across all tenant schemas.

Usage:
    python manage.py sync_admin_password --password=newpassword
"""
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context
from tenants.models import PrintShop


class Command(BaseCommand):
    help = 'Sync admin user password across all active tenant schemas'

    def add_arguments(self, parser):
        parser.add_argument('--password', required=True, help='New password for admin user')
        parser.add_argument('--username', default='anciappi', help='Admin username to sync')

    def handle(self, *args, **options):
        password = options['password']
        username = options['username']

        tenants = PrintShop.objects.exclude(schema_name='public')
        updated = 0
        errors = []

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.save()
                    self.stdout.write(f'  ✅ Updated in schema: {tenant.schema_name}')
                    updated += 1
                except User.DoesNotExist:
                    errors.append(tenant.schema_name)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Password synced across {updated} tenants.'
        ))

        if errors:
            self.stdout.write(self.style.WARNING(
                f'⚠️  User "{username}" not found in: {", ".join(errors)}'
            ))
