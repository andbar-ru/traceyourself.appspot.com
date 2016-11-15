# coding: utf-8
# Imports {{{1
from os import path
import logging
# app engine
import webapp2
from google.appengine.api import users, mail
# Шаблонизатор mako
from mako.lookup import TemplateLookup
TEMPLATES_DIR = path.join(path.dirname(__file__), 'templates')
lookup = TemplateLookup(
    directories=[TEMPLATES_DIR],
    input_encoding="utf-8",
    format_exceptions=True,
)
# проект
from forms import ContactForm
from lib.functions import get_i18n


#class Contacts(webapp2.RequestHandler) {{{1
class Contacts(webapp2.RequestHandler):

    #def get(self) {{{2
    def get(self, form=None, messageSent=False):
        # locale
        i18n = get_i18n(self.request)
        _ = i18n.gettext
        lang = i18n.locale

        # animation
        animation = self.request.cookies.get('animation', True)
        if animation == 'false':
            animation = False
        else: # 'true' или что-то странное
            animation = True

        action_url = "/contacts"

        # user
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)
        else:
            logout_url = users.create_login_url(self.request.uri)

        if form is None:
            form = ContactForm()

        template_values = {
            '_': _,
            'lang': lang,
            'animation': animation,
            'user': user,
            'logout_url': logout_url,
            'action_url': action_url,
            'form': form,
            'messageSent': messageSent,
            'route': '/contacts'
        }
        template = lookup.get_template("contacts.mako")
        self.response.write(template.render(**template_values))

    #def post(self) {{{2
    def post(self):
        if self.request.get('submit'):
            user = users.get_current_user()
            if user is None:
                U = 'Anonymous'
            else:
                U = user.email()

            form = ContactForm(self.request.POST)

            if form.validate():
                recipient = "info@traceyourself.com"
                sender = "Traceyourself contact <wind29121982@gmail.com>"
                subject = form.subject.data
                email = form.email.data
                cc = form.cc_myself.data
                if email:
                    email2answer = email
                else:
                    email2answer = u'не указан'
                
                body = u'Сообщение от %s.\n' % U
                body += u'Email для ответа: %s.\n\n' % email2answer
                body += form.message.data
                logging.warning(body)
                if user is not None and cc is True:
                    mail.send_mail(sender, recipient, subject, body, cc=U)
                else:
                    mail.send_mail(sender, recipient, subject, body)

                return self.get(messageSent=True)

            return self.get(form=form)




