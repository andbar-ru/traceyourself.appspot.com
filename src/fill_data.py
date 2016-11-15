# coding: utf-8
#Imports {{{1
from os import path
from datetime import date
import logging
# app engine
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
# Шаблонизатор mako
from mako.template import Template
from mako.lookup import TemplateLookup
TEMPLATES_DIR = path.join(path.dirname(__file__), 'templates')
lookup = TemplateLookup(
    directories=[TEMPLATES_DIR],
    input_encoding="utf-8",
    format_exceptions=True,
)
# проект
from models import *
import forms
from profile import build_residence
from lib.functions import get_i18n


# Global variables {{{1
empty_values = (None, '', []) # значения полей, при которых оно рассматривается как пустое


#class FillData(webapp2.RequestHandler) {{{1
class FillData(webapp2.RequestHandler):
    """/prof/fill_data"""
    #def __init__(self, *args, **kwargs) {{{2
    def __init__(self, *args, **kwargs):
        super(FillData, self).__init__(*args, **kwargs)
        self.WARNINGS = []

    def get(self, action=None, form=None, locationForm=None, Date=None): #{{{2
        """Предоставить пользователю форму для заполнения параметров.
        Отправляются только те данные, которые заполнены.
        form - форма с заполненными данными и ошибками
        Date - дата, за которую показывать значения
        """
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

        action_url = '/prof/fill_data'
        user = users.get_current_user()

        if user:    # Пользователь залогинен
            # Проверить, есть ли данный пользователь в нашем хранилище
            U = User.get_by_key_name(user.email())
            # ссылка для разлогинивания
            logout_url = users.create_logout_url(self.request.uri)

            # Если пользователь зарегистрирован
            if U:
                if not form:
                    form = forms.FillDataForm(U, Date=Date)
                residence = U.residence.name
                if locationForm is None:
                    locationForm = forms.LocationForm()

                template_values = {
                    '_': _,
                    'lang': lang,
                    'animation': animation,
                    'user': user, # login.mako
                    'logout_url': logout_url, # login.mako
                    'route': '/prof/fill_data',
                    'WARNINGS': self.WARNINGS,
                    'form': form,
                    'locationForm': locationForm,
                    'residence': residence,
                    'action_url': action_url,
                    'action': action
                }

                # Формируем и рендерим шаблон
                template = lookup.get_template("fill_data.mako")
                self.response.write(template.render(**template_values))
            # Если пользователь не зарегистрирован
            else:
                self.redirect("/prof")
        # Пользователь не залогинен
        else:
            self.redirect(users.create_login_url(self.request.uri))

    #def post(self) {{{2
    def post(self):
        """Заполнение тренда"""
        user = users.get_current_user()
        today = date.today()
        # два фиксированных параметра
        if user:
            U = User.get_by_key_name(user.email())
        else:
            return self.get()


        # Нажата кнопка "Сохранить" при выборе населённого пункта
        if self.request.get('submitLocationForm'):
            # получаем объект residence
            lang = self.request.get('lang')
            country = self.request.get('country')
            region = self.request.get('region')
            district = self.request.get('district')
            try:
                residence = build_residence(lang, country, region, district)
            except (IOError, KeyError): # Несовместимые пункты в select'ах
                return self.get()
            # строим форму
            form = forms.LocationForm(residence, formdata=self.request.POST)
            if form.validate():
                if form.locality.data: # если был запрос на изменение места жительства
                    name, id, url = form.locality.data.rsplit(';', 2)
                    keyname = "id_%s" % id
                    R = Residence.get_or_insert(keyname, id=int(id), name=name, url=url)
                    # Если м.ж. поменялось и у прежнего м.ж. это единственный пользователь, удаляем
                    if R.key() != U.residence.key() and U.residence.users.count() < 2:
                        U.residence.delete()
                    # Обязательные поля
                    U.residence = R
                    U.put()

                return self.get()
            else:
                return self.get(locationForm=form, action='editLocation')

        # Нажата кнопка "Обновить значения параметров"
        elif self.request.get('update_data'):
            form = forms.FillDataForm(U, formdata=self.request.POST)
            logging.warning(self.request.get('date'))

            if form.validate(): # Проверка пройдена (правда нужна только дата)
                Date = form.date.data
                return self.get(form=None, Date=Date)
            else:
                return self.get(form=form)

        # Нажата кнопка 'Занести значения'
        elif self.request.get('submit'):
            form = forms.FillDataForm(U, formdata=self.request.POST)
            logging.warning(self.request.get('date'))

            if form.validate(): # Проверка пройдена
                Date = form.date.data
                keyname = "%s_%s" % (U.nickname, Date.strftime("%Y%m%d"))
                UT = UserTrend.get_by_key_name(keyname, parent=U)
                if not UT:
                    ccd_key = "%s-%s" % (U.residence.key().name(), Date.strftime("%Y%m%d"))
                    UT = UserTrend(key_name=keyname, parent=U, date=today, ccd_key=ccd_key)

                all_values_are_empty = True # вначале все значения пустые

                # Подмена id не пройдёт, т.к. значения параметров и элементов берутся из валидированной формы
                for field in form:
                    if field.data not in empty_values:  # если значение есть
                        # 2 вида полей первого порядка (обычные и FormField)
                        if not hasattr(field, 'form'):  # обычный параметр
                            if field.name not in ('UTCdate', 'isToday'):
                                setattr(UT, field.name, field.data)
                                if field.name != 'date':
                                    all_values_are_empty = False
                        else:   # FormField (сложные параметры)
                            for subfield in field:
                                subfield_name = subfield.name.split('_')[1]
                                if subfield.data not in empty_values:   # если значение есть
                                    setattr(UT, subfield_name, subfield.data)
                                    all_values_are_empty = False
                                else:
                                    # если значение было, то свойство удаляется
                                    value = getattr(UT, subfield_name, None)
                                    if value not in empty_values:
                                        delattr(UT, subfield_name)
                    else:
                        # если значение было, то свойство удаляется
                        value = getattr(UT, field.name, None)
                        if value not in empty_values:
                            delattr(UT, field.name)

                if all_values_are_empty == True:
                    # пользователь не заполнил либо стёр данные, удаляем запись в хранилище
                    self.WARNINGS.append(u"Вы не заполнили данные")
                    db.delete(UT)
                else:
                    UT.put()
                    self.WARNINGS.append(u"Значения добавлены")

                return self.get(Date=Date)
            else:
                return self.get(form=form)


