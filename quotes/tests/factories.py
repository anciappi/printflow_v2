import factory
from factory.django import DjangoModelFactory
from users.models import User
from quotes.models import CardJobOrder

class PortalUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'portal_user_{n}')
    email = factory.Sequence(lambda n: f'portal_{n}@test.com')
    role = User.Roles.PORTAL
    is_active = True

class StaffUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'staff_user_{n}')
    email = factory.Sequence(lambda n: f'staff_{n}@test.com')
    role = User.Roles.ADMIN
    is_active = True

class CardJobOrderFactory(DjangoModelFactory):
    class Meta:
        model = CardJobOrder

    requester_name = factory.Faker('name')
    requester_email = factory.Faker('email')
    requester_phone = factory.Faker('phone_number')
    requester_cuit = '20-12345678-9'
    job_description = factory.Faker('sentence')
    front_colors = 'CMYK'
    status = 'DRAFT'
