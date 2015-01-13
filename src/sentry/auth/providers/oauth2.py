from __future__ import absolute_import, print_function

from urllib import urlencode
from uuid import uuid4

from sentry.auth import Provider, AuthView
from sentry.http import safe_urlopen, safe_urlread
from sentry.utils import json
from sentry.utils.http import absolute_uri

ERR_INVALID_STATE = 'An error occurred while validating your request.'


class OAuth2Login(AuthView):
    authorize_url = None
    client_id = None
    scope = ''

    def __init__(self, authorize_url=None, client_id=None, scope=None, *args,
                 **kwargs):
        super(OAuth2Login, self).__init__(*args, **kwargs)
        if authorize_url is not None:
            self.authorize_url = authorize_url
        if client_id is not None:
            self.client_id = client_id
        if scope is not None:
            self.scope = scope

    def get_scope(self):
        return self.scope

    def get_authorize_url(self):
        return self.authorize_url

    def get_authorize_params(self, state, redirect_uri):
        return {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.get_scope(),
            "state": state,
            "redirect_uri": redirect_uri,
        }

    def dispatch(self, request, provider):
        state = str(uuid4())

        params = self.get_authorized_params(
            state=state,
            redirect_uri=absolute_uri(self.get_next_url(request)),
        )

        redirect_uri = self.get_authorize_url() + '?' + urlencode(params)

        self.bind_state(request, 'state', state)

        return self.redirect(redirect_uri)


class OAuth2Callback(AuthView):
    access_token_url = None
    client_id = None
    client_secret = None

    def __init__(self, access_token_url=None, client_id=None,
                 client_secret=None, *args, **kwargs):
        super(OAuth2Login, self).__init__(*args, **kwargs)
        if access_token_url is not None:
            self.access_token_url = access_token_url
        if client_id is not None:
            self.client_id = client_id
        if client_secret is not None:
            self.client_secret = client_secret

    def get_token_params(self, code, redirect_uri):
        return {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

    def exchange_token(self, request, code):
        # TODO: this needs the auth yet
        params = self.get_token_params(
            code=code,
            redirect_uri=absolute_uri(self.get_current_url(request)),
        )
        req = safe_urlopen(self.access_token_url, data=params)
        body = safe_urlread(req)

        return json.loads(body)

    def dispatch(self, request, provider):
        error = request.GET.get('error')
        state = request.GET.get('state')
        code = request.GET.get('code')

        if error:
            return self.error(request, provider, error)

        if state != self.fetch_state(request, 'state'):
            return self.error(request, provider, ERR_INVALID_STATE)

        data = self.exchange_token(request, code)

        # we can either expect the API to be implicit and say "im looking for
        # blah within state data" or we need to pass implementation + call a
        # hook here
        self.bind_state(request, 'data', data)

        return self.next_step(request, provider)


class OAuth2Provider(Provider):
    def get_auth_pipeline(self):
        return [OAuth2Login(), OAuth2Callback()]
