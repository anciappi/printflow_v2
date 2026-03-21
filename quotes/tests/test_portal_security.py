"""
Security tests for portal role isolation.
Verifies that PORTAL users cannot access staff views
and that data ownership is enforced correctly.
"""
import pytest
from django.urls import reverse
from django.test import Client

from .factories import PortalUserFactory, StaffUserFactory, CardJobOrderFactory
from users.models import User


@pytest.mark.django_db
class TestPortalUserAccess:
    """PORTAL users can only access /portal/ URLs."""

    def test_portal_user_can_access_portal_home(self, auth_client, tenant):
        """Verifies that a PORTAL user can successfully load the portal home."""
        user = PortalUserFactory(password='testpass123', tenant=tenant)
        client = auth_client(user)
        response = client.get(reverse('quotes:portal_home'))
        assert response.status_code == 200

    def test_portal_user_cannot_access_inventory(self, auth_client, tenant):
        """Verifies that a PORTAL user is redirected away from inventory views."""
        user = PortalUserFactory(tenant=tenant)
        client = auth_client(user)
        response = client.get('/inventory/unidades/')
        assert response.status_code in [302, 403]
        assert 'portal' in response.url

    def test_portal_user_cannot_access_card_job_list(self, auth_client, tenant):
        """Verifies that a PORTAL user cannot access the staff card jobs internal list."""
        user = PortalUserFactory(tenant=tenant)
        client = auth_client(user)
        response = client.get('/portal/card-jobs/')
        assert response.status_code in [302, 403]

    def test_portal_user_cannot_access_purchasing(self, auth_client, tenant):
        """Verifies that a PORTAL user is redirected away from purchasing module."""
        user = PortalUserFactory(tenant=tenant)
        client = auth_client(user)
        response = client.get('/purchasing/')
        assert response.status_code in [302, 403]
        assert 'portal' in response.url

    def test_portal_user_cannot_access_customers(self, auth_client, tenant):
        """Verifies that a PORTAL user is redirected away from customers module."""
        user = PortalUserFactory(tenant=tenant)
        client = auth_client(user)
        response = client.get('/customers/')
        assert response.status_code in [302, 403]
        assert 'portal' in response.url


@pytest.mark.django_db
class TestStaffUserAccess:
    """STAFF users have full access to all URLs."""

    def test_staff_can_access_inventory(self, auth_client, tenant):
        """Verifies that a STAFF user is allowed access to the inventory."""
        user = StaffUserFactory(tenant=tenant)
        client = auth_client(user)
        response = client.get('/inventory/unidades/')
        assert response.status_code == 200

    def test_staff_can_access_card_job_list(self, auth_client, tenant):
        """Verifies that a STAFF user can view the internal card job lists."""
        user = StaffUserFactory(tenant=tenant)
        client = auth_client(user)
        response = client.get('/portal/card-jobs/')
        assert response.status_code == 200

    def test_staff_can_access_portal_home(self, auth_client, tenant):
        """Verifies that a STAFF user is correctly redirected away from the client portal home and sent to dashboard."""
        user = StaffUserFactory(tenant=tenant)
        client = auth_client(user)
        # Staff should be redirected away from client portal home
        response = client.get('/portal/')
        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestCardJobOwnership:
    """Portal users can only see their own orders."""

    def test_portal_user_sees_own_orders(self, auth_client, tenant):
        """Verifies that a PORTAL user can see jobs assigned to them in context."""
        user = PortalUserFactory(tenant=tenant)
        own_job = CardJobOrderFactory(portal_user=user)
        client = auth_client(user)
        response = client.get(reverse('quotes:portal_home'))
        assert own_job in response.context['card_jobs']

    def test_portal_user_cannot_see_other_users_orders(self, auth_client, tenant):
        """Verifies that a PORTAL user does NOT see jobs belonging to another user in context."""
        user = PortalUserFactory(tenant=tenant)
        other_user = PortalUserFactory(tenant=tenant)
        other_job = CardJobOrderFactory(portal_user=other_user)
        client = auth_client(user)
        response = client.get(reverse('quotes:portal_home'))
        assert other_job not in response.context['card_jobs']

    def test_portal_user_cannot_access_other_users_detail(self, auth_client, tenant):
        """Verifies that a PORTAL user is redirected when trying to view another user's job details."""
        user = PortalUserFactory(tenant=tenant)
        other_user = PortalUserFactory(tenant=tenant)
        other_job = CardJobOrderFactory(portal_user=other_user)
        client = auth_client(user)
        response = client.get(reverse('quotes:card_job_detail', kwargs={'pk': other_job.pk}))
        assert response.status_code in [302, 403]
        assert response.url == reverse('quotes:portal_home')

    def test_portal_user_can_access_own_detail(self, auth_client, tenant):
        """Verifies that a PORTAL user can successfully view their own job details."""
        user = PortalUserFactory(tenant=tenant)
        own_job = CardJobOrderFactory(portal_user=user)
        client = auth_client(user)
        response = client.get(reverse('quotes:card_job_detail', kwargs={'pk': own_job.pk}))
        assert response.status_code == 200


@pytest.mark.django_db
class TestPortalCreateUser:
    """Staff can create portal users — PORTAL users cannot."""

    def test_staff_can_create_portal_user(self, auth_client, tenant):
        """Verifies that a STAFF user can successfully create a new portal user."""
        staff = StaffUserFactory(tenant=tenant)
        client = auth_client(staff)
        response = client.post(reverse('quotes:portal_create_user'), {
            'email': 'newclient@test.com',
            'full_name': 'Juan Perez',
        })
        assert response.status_code == 200
        assert User.objects.filter(email='newclient@test.com', role=User.Roles.PORTAL).exists()

    def test_portal_user_cannot_create_portal_user(self, auth_client, tenant):
        """Verifies that a PORTAL user gets blocked/redirected when attempting to create a new portal user."""
        portal = PortalUserFactory(tenant=tenant)
        client = auth_client(portal)
        response = client.post(reverse('quotes:portal_create_user'), {
            'email': 'hacker@test.com',
            'full_name': 'Hacker',
        })
        assert response.status_code in [302, 403]
        assert not User.objects.filter(email='hacker@test.com').exists()

    def test_duplicate_email_rejected(self, auth_client, tenant):
        """Verifies that creating a portal user with an existing email returns an error context."""
        staff = StaffUserFactory(tenant=tenant)
        existing = PortalUserFactory(email='existing@test.com', tenant=tenant)
        client = auth_client(staff)
        response = client.post(reverse('quotes:portal_create_user'), {
            'email': 'existing@test.com',
            'full_name': 'Duplicate',
        })
        assert response.status_code == 200
        assert 'error' in response.context
