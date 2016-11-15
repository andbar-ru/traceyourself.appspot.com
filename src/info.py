#coding: utf-8
import os

import webapp2
from google.appengine.ext import db

# Шаблонизатор mako
from mako.template import Template
from mako.lookup import TemplateLookup
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
lookup = TemplateLookup(directories=[TEMPLATES_DIR],
						input_encoding="utf-8")

import models


class Count(webapp2.RequestHandler):

	def get(self, model=None):
		"""Показываем страничку, на которой админ может выбрать модель,
		количество объектов в которой необходимо узнать"""
		Models = []
		for name, obj in models.__dict__.iteritems():
			try:
				base = obj.__bases__[0]	# Родитель класса
				if base is db.Model or base is db.Expando:
					if obj.all().get():	# Нас не интересуют пустые модели
						Models.append(name)
			except AttributeError:
				pass

		template_values = {
			'models': Models,
			'model_info': model,
		}
		template = lookup.get_template("info_count.mako")
		self.response.write(template.render(**template_values))

	def post(self):
		model = self.request.get("model")
		Query = getattr(models, model).all()
		count = Query.count(limit=None)

		return self.get(model=(model, count))


app = webapp2.WSGIApplication([
	('/info/count', Count),
], debug=True)

