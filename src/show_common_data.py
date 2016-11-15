#coding: utf-8
#Imports {{{1
import os
import webapp2
import logging
# Шаблонизатор mako
from mako.lookup import TemplateLookup
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
lookup = TemplateLookup(directories=[TEMPLATES_DIR], input_encoding="utf-8", format_exceptions=True)

from models import *
from ajax import all_common_properties
from lib.functions import get_i18n
import forms

#}}}
class ShowCommonData(webapp2.RequestHandler): #{{{1
    """Показать общие данные"""
    def get(self, commonDataForm=None): #{{{2
        # locale
        i18n = get_i18n(self.request)
        _ = i18n.gettext
        lang = i18n.locale

        if commonDataForm is None:
            commonDataForm = forms.CommonDataForm()

        # Выдать данные
        template_values = {
            '_': _,
            'lang': lang,
            'render_field': forms.render_field,
            'commonDataForm': commonDataForm
        }

        # Формируем и рендерим шаблон
        template = lookup.get_template('show_common_data.mako')
        self.response.write(template.render(**template_values))
    #}}}
#}}}
app = webapp2.WSGIApplication([ #{{{1
                               ('/show_common_data', ShowCommonData),
                              ], debug=True)

