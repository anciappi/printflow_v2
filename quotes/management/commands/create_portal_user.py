from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Creates the default portal user (PORTAL role)'

    def add_arguments(self, parser):
        parser.add_argument('password', type=str, help='Password for the portal user')

    def handle(self, *args, **kwargs):
        password = kwargs['password']
        email = 'portal@printflow.com'
        username = 'portal_client'

        # Check if user exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists.'))
            user = User.objects.get(email=email)
            user.set_password(password)
            user.role = User.Roles.PORTAL
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated password and role for existing user {email}.'))
            return

        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=User.Roles.PORTAL,
            first_name='Portal',
            last_name='Access'
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created portal user: {email}'))
