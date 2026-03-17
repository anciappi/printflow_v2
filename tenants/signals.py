import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tenants.utils import schema_context
from .models import PrintShop


@receiver(post_save, sender=PrintShop)
def create_admin_in_new_tenant(sender, instance, created, **kwargs):
    if not created or instance.schema_name == 'public':
        return
    # Signal only fires in production (Django Admin)
    # reset_app.sh handles dev environment
    pass
