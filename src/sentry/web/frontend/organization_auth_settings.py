from __future__ import absolute_import

from django import forms

from sentry.auth import providers
from sentry.models import (
    AuditLogEntry, AuditLogEntryEvent, Organization, OrganizationMemberType
)
from sentry.web.frontend.base import OrganizationView


class OrganizationAuthSettingsView(OrganizationView):
    required_access = OrganizationMemberType.OWNER

    def handle(self, request, organization):
        context = {
            'provider_list': providers,
        }

        return self.respond('sentry/organization-auth-settings.html', context)
