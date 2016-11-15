#coding: utf-8
import os
import cPickle
from glob import glob

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


class UploadData(webapp2.RequestHandler):
	"""Предоставляет выбор сериализованного файла, десериализовывает строку и записывает объекты
	в хранилище.
	Аналог appcfg.py upload_data.
	"""
	def get(self):
		files = glob('resources/*.pickle')
		template_values = {
			'files': files,
		}
		template = lookup.get_template("upload_data.mako")
		self.response.write(template.render(**template_values))


	def post(self):
		file = self.request.get('file')
		F = open(file)
		S = F.read()
		F.close()

		obj = cPickle.loads(S)
		modelname = obj['model']
		model = getattr(models, modelname)
		entities = obj['entities']
		count = 0
		for e in entities:
			kwargs = {
				'key_name': e['keyname'],
				'key': Key.from_path(*e['key']),
				'parent': (Key.from_path(*e['parent']) if e['parent'] else None)
			}
			# Свойства
			for field, value in e['fields'].iteritems():
				if type(value) is tuple:
					if value[0] == 'key':
						value = Key.from_path(*value[1])
					else:
						value = value[1]
				kwargs[field] = value
			entity = model(**kwargs)
			entity.put()
			count += 1

		self.response.write('%d entities have been put into the model "%s"' % (count, modelname))



app = webapp2.WSGIApplication([
	('/upload_data', UploadData),
], debug=True)

