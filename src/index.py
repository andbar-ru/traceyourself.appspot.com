# coding: utf-8
# Imports {{{1
import webapp2
# classes
from about import About
from contacts import Contacts
from profile import Profile, GetRegions, GetDistricts, GetLocalities
from fill_data import FillData
from analysis import Analysis, AnalysisSaved, AnalysisTest


# app = webapp2.WSGIApplication(... {{{1
app = webapp2.WSGIApplication([
    ('/', About),
    ('/contacts', Contacts),
    ('/prof', Profile),
    ('/prof/fill_data', FillData),
    webapp2.Route('/analysis', Analysis),
    webapp2.Route('/analysis/<user>', Analysis), # admin only
    ('/analysis_saved', AnalysisSaved),
    ('/analysis_test', AnalysisTest),
    ('/get_regions', GetRegions),
    ('/get_districts', GetDistricts),
    ('/get_localities', GetLocalities),
], debug=True)
