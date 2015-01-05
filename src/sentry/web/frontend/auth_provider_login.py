from __future__ import absolute_import, print_function

from django.contrib.auth import login
from django.conf import settings

from sentry.web.forms.accounts import AuthenticationForm
from sentry.web.frontend.base import BaseView
from sentry.utils.auth import get_auth_providers, get_login_redirect


class AuthProviderLoginView(BaseView):
    auth_required = False

    def handle(self, request, organization_id):
        provider = None # TODO

        pipeline = provider.get_auth_pipeline()

        return self.respond('sentry/auth-provider-login.html', context)
