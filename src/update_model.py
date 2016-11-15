#coding: utf-8
import os
from time import time as T
import logging
import webapp2
from google.appengine.ext import db
from google.appengine.runtime import DeadlineExceededError
# Шаблонизатор mako
from mako.lookup import TemplateLookup
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
lookup = TemplateLookup(directories=[TEMPLATES_DIR], input_encoding="utf-8", format_exceptions=True)

import models


class UpdateModel(webapp2.RequestHandler):
    """Обновить модель, чтобы заработали индексы на свойствах или, наоборот, перестали работать."""
    def get(self):
        """Показываем страничку, c формой, где админ должен ввести имя модели,
        которую следует обновить."""
        # Формируем и рендерим шаблон
        template = lookup.get_template('update_model.mako')
        self.response.write(template.render())


    def post(self):
        T0 = T()

        modelname = self.request.get('model')
        if not modelname:
            self.response.write(u"Не задана модель<br>\n")
            return

        model = getattr(models, modelname)
        entities = list(model.all()) # Запрос может жить только 30 сек.
        for e in entities:
            e.put()

        T1 = T()
        self.response.write("It has been taken %.2f sec.<br>\n" % (T1-T0))


app = webapp2.WSGIApplication([
                               ('/update_model', UpdateModel),
                              ], debug=True)

