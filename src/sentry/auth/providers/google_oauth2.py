from __future__ import absolute_import, print_function

from django.conf import settings
from urllib import urlencode

from sentry.auth import AuthView
from sentry.auth.providers.oauth2 import (
    OAuth2Callback, OAuth2Provider, OAuth2Login
)
from sentry.http import safe_urlopen, safe_urlread
from sentry.utils import json

AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'

ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

SCOPE = 'email'

CLIENT_ID = getattr(settings, 'GOOGLE_CLIENT_ID', None)

CLIENT_SECRET = getattr(settings, 'GOOGLE_CLIENT_SECRET', None)

USER_DETAILS_ENDPOINT = 'https://www.googleapis.com/plus/v1/people/me'

ERR_INVALID_DOMAIN = 'The domain for your Google account is not allowed to authenticate with this provider.'


class FetchUser(AuthView):
    def __init__(self, domain=None, *args, **kwargs):
        self.domain = domain
        super(FetchUser, self).__init__(*args, **kwargs)

    def dispatch(self, request, provider):
        access_token = self.fetch_state(request, 'data')['access_token']

        req = safe_urlopen('{0}?{1}'.format(
            USER_DETAILS_ENDPOINT,
            urlencode({
                'access_token': access_token,
            }),
        ))
        body = safe_urlread(req)
        data = json.loads(body)

        if self.domain and self.domain != data['domain']:
            return self.error(request, provider, ERR_INVALID_DOMAIN)

        self.bind_state(request, 'user', data)

        return self.next_step(request, provider)


class GoogleOAuth2Provider(OAuth2Provider):
    def __init__(self, domain=None, **config):
        self.domain = domain
        super(GoogleOAuth2Provider, self).__init__(**config)

    def get_auth_pipeline(self):
        return [
            OAuth2Login(
                authorize_url=AUTHORIZE_URL,
                scope=SCOPE,
                client_id=CLIENT_ID,
            ),
            OAuth2Callback(
                access_token_url=ACCESS_TOKEN_URL,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
            ),
            FetchUser(domain=self.domain),
        ]

    def get_identity(self, state):
        # data.user => {
        #   "displayName": "David Cramer",
        #   "emails": [{"value": "david@getsentry.com", "type": "account"}],
        #   "domain": "getsentry.com",
        #   "verified": false
        # }
        user_data = state['user']
        return {
            # TODO: is there a "correct" email?
            'email': user_data['emails'][0]['value'],
            'name': user_data['displayName'],
        }
