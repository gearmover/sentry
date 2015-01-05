from __future__ import absolute_import, print_function

__all__ = ('AuthView',)

from sentry.web.frontend.base import BaseView


class AuthView(BaseView):
    auth_required = False
    sudo_required = False

    def dispatch(self, request, provider):
        """
        Returns an ``HttpResponse``.
        """
        raise NotImplementedError

    def get_next_url(self, request, provider):
        # each step url should be something like md5(cls_path)
        return request.path

    def get_current_url(self, request, provider):
        return request.path

    def next_step(self, request, provider):
        # TODO: this needs to somehow embed the next step
        # (it shouldnt force an exteneral redirect)
        return self.redirect(self.get_next_url())

    def error(self, request, provider, message):
        raise NotImplementedError

    def bind_state(self, request, key, value):
        raise NotImplementedError

    def fetch_state(self, request, key, value):
        raise NotImplementedError
