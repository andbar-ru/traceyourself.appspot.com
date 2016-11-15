# coding: utf-8
#Imports {{{1
import webapp2
from os import path
import logging

# mako
from mako.template import Template
from mako.lookup import TemplateLookup
TEMPLATES_DIR = path.join(path.dirname(__file__), 'templates')
lookup = TemplateLookup(
    directories=[TEMPLATES_DIR],
    input_encoding="utf-8",
    format_exceptions=True,
)

from models import *

#class Test(webapp2.RequestHandler) {{{1
class Test(webapp2.RequestHandler):
    def get(self):
        import forms
        form = forms.LocationForm()

        template_values = {
            'form': form
        }

        template = lookup.get_template("test.mako")
        self.response.write(template.render(**template_values))


# app = webapp2.WSGIApplication(...) {{{1
app = webapp2.WSGIApplication([
   webapp2.Route(r'/test', Test),
   webapp2.Route(r'/test/<param>', Test),
], debug=True)
