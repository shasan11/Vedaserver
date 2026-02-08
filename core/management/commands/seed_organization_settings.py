from django.core.management.base import BaseCommand
from django.db import transaction

from settings.models import Organization, OrganizationSettings


DEFAULT_ORG_CODE = "default"
DEFAULT_ORG_NAME = "Default Organization"

DEFAULT_SETTINGS = {
    "branding": {"theme": "light"},
    "general": {"timezone": "Asia/Kathmandu", "language": "en"},
    "security": {},
    "mail": {},
    "sms": {},
    "storage": {},
    "media_protection": {},
    "payments": {},
}


class Command(BaseCommand):
    help = "Seed default organization and organization settings if they do not exist."

    def handle(self, *args, **options):
        with transaction.atomic():
            org = self._ensure_default_organization()
            self._ensure_settings_for_orgs(fallback_org=org)

    def _ensure_default_organization(self):
        if Organization.objects.exists():
            self.stdout.write(self.style.WARNING("Organizations already exist. Skipping default org seed."))
            return Organization.objects.order_by("created").first()

        org = Organization.objects.create(
            name=DEFAULT_ORG_NAME,
            code=DEFAULT_ORG_CODE,
            is_system_generated=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Created default organization: {org.name}"))
        return org

    def _ensure_settings_for_orgs(self, fallback_org=None):
        orgs = Organization.objects.all()
        if not orgs.exists() and fallback_org is not None:
            orgs = Organization.objects.filter(pk=fallback_org.pk)

        for org in orgs:
            settings, created = OrganizationSettings.objects.get_or_create(
                organization=org,
                defaults={
                    "is_system_generated": True,
                    **DEFAULT_SETTINGS,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created settings for organization: {org.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Settings already exist for organization: {org.name}"
                    )
                )
