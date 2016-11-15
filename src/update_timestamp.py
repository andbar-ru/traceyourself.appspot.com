# coding: utf-8
#Imports {{{1
import webapp2


#class UpdateTimestamp(webapp2.RequestHandler) {{{1
class UpdateTimestamp(webapp2.RequestHandler):
    #def get(self) {{{2
    def get(self):
        with open('update_timestamp') as F:
            for line in F.readlines():
                self.response.write("%s<br>" % line)


# app = webapp2.WSGIApplication(...) {{{1
app = webapp2.WSGIApplication([
   ('/update_timestamp', UpdateTimestamp),
], debug=True)
