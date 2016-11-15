#coding: utf-8

# Если понадобится выводить объекты в виде строки

from pprint import PrettyPrinter
from collections import OrderedDict
import logging

class UnicodePrettyPrinter(PrettyPrinter):
    def pformat(self, object):
        if isinstance(object, OrderedDict):
            object = dict(object)
        return PrettyPrinter.pformat(self, object)

    def format(self, object, context, maxlevels, level):
        repr, readable, recursive = PrettyPrinter.format(self, object, context, maxlevels, level)
        if repr and isinstance(repr, (str, unicode)):
            repr = repr.decode('unicode_escape').encode('utf-8')
        return repr, readable, recursive

pformat = UnicodePrettyPrinter(indent=1, width=100).pformat

