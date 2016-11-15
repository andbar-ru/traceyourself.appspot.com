# coding: utf-8
# Imports {{{1
from os import path
import logging
# app engine
import webapp2
from google.appengine.api import users
# Шаблонизатор mako
from mako.lookup import TemplateLookup
TEMPLATES_DIR = path.join(path.dirname(__file__), 'templates')
lookup = TemplateLookup(
    directories=[TEMPLATES_DIR],
    input_encoding="utf-8",
    format_exceptions=True,
)
# проект
from lib.functions import get_i18n


class About(webapp2.RequestHandler): #{{{1

    def get(self): #{{{2
        # locale
        i18n = get_i18n(self.request)
        _ = i18n.gettext
        lang = i18n.locale

        # animation
        animation = self.request.cookies.get('animation', True)
        if animation == 'false':
            animation = False
        else: # 'true' или что-то странное
            animation = True

        # user
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)
        else:
            logout_url = users.create_login_url(self.request.uri)

        template_values = {
            '_': _,
            'lang': lang,
            'animation': animation,
            'user': user,
            'logout_url': logout_url,
            'route': '/'
        }
        template = lookup.get_template("about.mako")
        self.response.write(template.render(**template_values))



