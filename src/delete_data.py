#coding: utf-8
import os
from time import time as T
import logging
import webapp2
from google.appengine.ext import db
# Шаблонизатор mako
from mako.lookup import TemplateLookup
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
lookup = TemplateLookup(directories=[TEMPLATES_DIR], input_encoding="utf-8", format_exceptions=True)

import models


class DeleteModel(webapp2.RequestHandler):

    def get(self, cleared=None):
        """Показываем страничку, на которой админ может выбрать модель,
        которую следует очистить"""
        models_to_clear = []
        for name, obj in models.__dict__.iteritems():
            try:
                base = obj.__bases__[0] # Родитель класса
                if base is db.Model or base is db.Expando:
                    if obj.all().get(): # Нас не интересуют пустые модели
                        models_to_clear.append(name)
            except AttributeError:
                pass

        template_values = {
            'models': models_to_clear,
            'cleared': cleared
        }

        # Формируем и рендерим шаблон
        template = lookup.get_template("delete_model.mako")
        self.response.write(template.render(**template_values))

    def post(self):
        model = self.request.get("model")
        Query = getattr(models, model).all()
        db.delete(Query)
        logging.warning("Model %s has been cleared" % model)

        return self.get(cleared=model)


class DeleteModelAttr(webapp2.RequestHandler):
    def get(self):
        """Показываем страничку, c формой, где админ должен ввести имя модели и свойство,
        которое следует удалить у модели.
        ВНИМАНИЕ: На время проведения операции удаления модель должна наследоваться от db.Expando.
        Потом, если необхдимо, можно вернуть обратно.
        """
        # Формируем и рендерим шаблон
        template = lookup.get_template('delete_model_attr.mako')
        self.response.write(template.render())

    def post(self):
        T0 = T()

        WARNING = ''
        modelname = self.request.get('model')
        attr = self.request.get('attr')
        if not modelname:
            self.response.write(u"Не задана модель<br>\n")
            return
        elif not attr:
            self.response.write(u"Не задано свойство<br>\n")
            return

        model = getattr(models, modelname)
        if model.__bases__[0].__name__ != 'Expando':
            self.response.write(u"Модель %s не наследуется от db.Expando<br>\n" % modelname)
            return
        elif attr in model.fields().keys():
            self.response.write(u"Свойство %s является статичным<br>\n" % attr)
            return

        entities = model.all()

        for e in entities:
            try:
                delattr(e, attr)
                e.put()
            except AttributeError: # такого свойства у объекта нет
                WARNING = u'У некоторых или у всех объектов модели `%s` не было свойства `%s`.' % (modelname, attr)
                continue

        if WARNING:
            self.response.write(WARNING)

        T1 = T()
        self.response.write("It has been taken %.2f sec.<br>\n" % (T1-T0))


class DeleteUser(webapp2.RequestHandler):

    def get(self, cleared=None):
        """Показываем страничку, на которой админ может выбрать пользователя,
        профиль которого следует удалить вместе с данными.
        """
        Us = models.User.all()

        template_values = {
            'users': Us,
            'cleared': cleared
        }

        # Формируем и рендерим шаблон
        template = lookup.get_template("delete_user.mako")
        self.response.write(template.render(**template_values))

    def post(self):
        user_keyname = self.request.get('user')
        logging.warning(u"Удаляем пользователя %s вместе со всеми данными" % user_keyname)
        U = models.User.get_by_key_name(user_keyname)
        # Удалить все данные пользователя
        db.delete(db.query_descendants(U))
        # если в месте жительства пользователя зарегистрирован только он один, удаляем
        residence = U.residence
        if residence.users.count() < 2:
            residence.delete()
        # И наконец удаляем профиль
        cleared = U.nickname
        U.delete()

        return self.get(cleared=cleared)


app = webapp2.WSGIApplication([
                               ('/delete_data/model', DeleteModel),
                               ('/delete_data/model_attr', DeleteModelAttr),
                               ('/delete_data/user', DeleteUser),
                              ], debug=True)

