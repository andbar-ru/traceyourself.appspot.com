#coding: utf-8
import os
import cPickle
import logging

import webapp2
from google.appengine.ext import db
from google.appengine.api.datastore_types import Key

# Шаблонизатор mako
from mako.template import Template
from mako.lookup import TemplateLookup
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
lookup = TemplateLookup(directories=[TEMPLATES_DIR],
                        input_encoding="utf-8")

import models


class DownloadData(webapp2.RequestHandler):
    """Предоставляет выбор модели и представляет её в сериализованной форме.
    Аналог appcfg.py download_data.
    """

    def get(self):
        Models = []
        for name, obj in models.__dict__.iteritems():
            try:
                base = obj.__bases__[0] # Родитель класса
                if base is db.Model or base is db.Expando:
                    Models.append(name)
            except AttributeError:
                pass

        template_values = {
            'models': Models,
        }
        template = lookup.get_template("download_data.mako")
        self.response.write(template.render(**template_values))

    def post(self):
        how = self.request.get('how')

        if how == 'all':
            model = self.request.get("model")
            entities = getattr(models, model).all()
        elif how == 'query':
            model = self.request.get("qModel")
            condition = self.request.get("condition")
            query = 'SELECT * FROM %s %s' % (model, condition)
            entities = db.GqlQuery(query)

        ser_obj = {'model':model, 'entities':[]} # сериализуемый объект

        for e in entities:
            obj = {
                'key': e.key().to_path(),
                'keyname': e.key().name(),
                'parent': (e.parent().key().to_path() if e.parent() else None),
                'fields': {}
            }
            # Статичные свойства
            fields = e.fields().keys()            # статичные свойства
            fields.extend(e.dynamic_properties()) # динамические свойства
            for field in fields:
                value = getattr(e, field)
                # значения ссылки преобразуем в путь ключа
                if isinstance(value, db.Model):
                    value = ('key', value.key().to_path())
                obj['fields'][field] = value

            ser_obj['entities'].append(obj)

        S = cPickle.dumps(ser_obj)
        self.response.write(S)


app = webapp2.WSGIApplication([
    ('/download_data', DownloadData)
], debug=True)

