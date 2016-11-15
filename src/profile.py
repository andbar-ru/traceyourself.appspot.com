# coding: utf-8
#Imports {{{1
from os import path
import json
from datetime import date
import logging
# GAE
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
# Шаблонизатор mako
from mako.lookup import TemplateLookup
TEMPLATES_DIR = path.join(path.dirname(__file__), 'templates')
lookup = TemplateLookup(
    directories=[TEMPLATES_DIR],
    input_encoding="utf-8",
    format_exceptions=True,
)
# Проект
from models import *
import forms
from lib.functions import get_i18n

#Global variables {{{1
RP5_DIR = './rp5'
types_with_measure = ('int', 'float') # типы параметров/элементов, к которым применимо понятие "Единицы измерения"
empty_values = (None, '', []) # значения полей, при которых оно рассматривается как пустое

#def build_residence(lang, country=None, region=None, district=None) {{{1
def build_residence(lang, country=None, region=None, district=None):
    """Вспомогательная функция, нужна для формирования диалога выбора места проживания.
    country, region и district - имена ключей (составные названия), а не свойство name объектов.
    Возвращает экземпляр класса Residence."""
    if lang not in ('ru', 'en'):
        lang = 'ru'

    class Residence(object):
        pass

    residence = Residence()

    if country:
        # получаем регионы
        residence.country = country
        countryNode = path.join(RP5_DIR, lang, country)
        # большая страна
        if path.isdir(countryNode):
            regionsFile = path.join(countryNode, 'regions')
            with open(regionsFile) as F:
                regionsDict = json.load(F)
            regions = [(d,name) for name,d in regionsDict.iteritems()]
            residence.all_regions = False
        # малая страна
        elif path.isfile(countryNode):
            with open(countryNode) as F:
                regionsDict = json.load(F)
            regions = [(name,name) for name in regionsDict.iterkeys() if name != 'allLocations']
            residence.all_regions = True

        regions.sort(key=lambda t: t[1])
        residence.regions = regions

        if region:
            residence.region = region
            if region == 'ALL':
                # получаем все н.п. страны
                locations = []
                for name,id,url in regionsDict['allLocations']:
                    value = '%s;%s;%s' % (name, id, url) # составной value для option
                    locations.append( (value,name) )
                residence.localities = locations
            else:
                if region.isdigit():
                    # получаем районы
                    districtsFile = path.join(countryNode, region)
                    with open(districtsFile) as F:
                        districtsDict = json.load(F)
                    districts = [(name,name) for name in districtsDict.iterkeys() if name != 'allLocations']
                    districts.sort(key=lambda t: t[1])
                    residence.districts = districts
                else:
                    # получаем все н.п. региона
                    locations = []
                    for location in regionsDict[region]:
                        name,id,url = location[:3]
                        value = '%s;%s;%s' % (name, id, url)
                        locations.append( (value,name) )
                    residence.localities = locations

        if district:
            residence.district = district
            if district == 'ALL':
                # получаем все н.п. региона
                locations = []
                for name,id,url in districtsDict['allLocations']:
                    value = '%s;%s;%s' % (name, id, url)
                    locations.append( (value,name) )
                residence.localities = locations
            else:
                # получаем н.п. района
                locations = []
                for name,id,url in districtsDict[district]:
                    value = '%s;%s;%s' % (name, id, url)
                    locations.append( (value,name) )
                residence.localities = locations

    else: # if country
        return
    # В возвращаемом объекте м.б. не все свойства
    return residence
#}}}
#def change_type(prop, new_type) {{{1
def change_type(prop, new_type):
    """Меняет тип ${prop} на new_type, если это допустимо:
    Типы int, float и scale можно взаимно менять. Это всё числа.
    Остальные типы менять нельзя.
    """
    if prop.type in ('scale', 'int', 'float') and new_type in ('scale', 'int', 'float'):
        prop.type = new_type
    else:
        pass
#}}}
class Profile(webapp2.RequestHandler): #{{{1

    def get(self, action=None, residence=None, form=None, commonPropsForm=None): #{{{2
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

        # user
        user = users.get_current_user()
        logout_url = users.create_logout_url(self.request.uri)
        action_url = "/prof"

        if user:    # Пользователь залогинен
            # Проверить, есть ли данный пользователь в нашем хранилище
            U = User.get_by_key_name(user.email())
            # Если пользователь зарегистрирован, то вывести его данные
            if U:
                # общие параметры
                if not commonPropsForm:
                    commonProps = {
                        'indiceProps': [],
                        'commodityProps': [],
                        'currencyProps': [],
                        'astroProps': set(),
                        'geomagneticProps': [],
                        'weatherProps': []
                    }
                    for p in U.common_props: # отмеченные общие параметры
                        if p.startswith('Indice'):
                            commonProps['indiceProps'].append(p)
                        elif p.startswith('Commodity'):
                            commonProps['commodityProps'].append(p)
                        elif p.startswith('Currency'):
                            commonProps['currencyProps'].append(p)
                        elif p.startswith('AstroData'):
                            commonProps['astroProps'].add(p.split('_')[0])
                        elif p.startswith('CommonData'):
                            commonProps['geomagneticProps'].append(p)
                        elif p.startswith('CommonCityData'):
                            commonProps['weatherProps'].append(p)
                    commonPropsForm = forms.CommonProperties(**commonProps)
                # параметры пользователя (GqlQuery object)
                props = Prop.all().ancestor(U).order('order')
                # формы, раскиданные по странице
                page_forms = {
                    'profileForm': forms.ProfileForm(obj=U, lang=lang),
                    'commonPropsForm': commonPropsForm,
                    'prop_edit_forms': {},
                    'add_prop_form': forms.Add_prop(),
                }
                for prop in props:
                    prop_id = prop.key().id()
                    # форма редактирования параметра
                    page_forms['prop_edit_forms'][prop_id] = forms.Edit_prop(prop)

                template_values = {
                    '_': _,
                    'lang': lang,
                    'animation': animation,
                    'title': _(u'Настройки профиля'),
                    'user': user,
                    'logout_url': logout_url,
                    'route': '/prof',
                    'U': U,
                    'props': props,
                    'action_url': action_url,
                    'action': action,
                    'form': form,
                    'forms': page_forms
                }
            else: # if U
                # Предоставляем форму для заполнения личных данных
                page_forms = {
                    'profileForm': forms.ProfileForm(lang=lang)
                }

                template_values = {
                    '_': _,
                    'lang': lang,
                    'animation': animation,
                    'title': _(u'Создание профиля'),
                    'user': user,
                    'logout_url': logout_url,
                    'action_url': action_url,
                    'route': '/prof',
                    'forms': page_forms,
                    'form': form
                }
            # Формируем и рендерим шаблон
            template = lookup.get_template("profile.mako")
            self.response.write(template.render(**template_values))
        # перенаправление на страницу логина google
        else: # if user
            return self.redirect(users.create_login_url(self.request.uri))


    def post(self): #{{{2
        """Обработка нажатий различных кнопок type=submit"""
        user = users.get_current_user()
        U = User.get_by_key_name(user.email())

        if self.request.get('submit_static'): #{{{3
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
            form = forms.ProfileForm(residence, formdata=self.request.POST)
            if form.validate():
                # всё правильно, заносим данные в хранилище
                name, id, url = form.locality.data.rsplit(';', 2)
                keyname = "id_%s" % id
                R = Residence.get_or_insert(keyname, id=int(id), name=name, url=url)
                # Статические данные пользователя (Модель User)
                U = User(
                    key_name = user.email(),
                    user_obj = user,
                    nickname = user.nickname(),
                    residence = R
                )
                # Необязательные для заполнения поля
                for prop in ('name', 'surname', 'patronymic', 'gender'):
                    field = getattr(form, prop)
                    setattr(U, prop, field.data)
                if form.birthdate.data['year']: # данные по дате либо все, либо ни одной
                    b_data = form.birthdate.data
                    U.birthdate = date(int(b_data['year']), int(b_data['month']), int(b_data['day']))
                # Помещаем объект в хранилище
                U.put()

                return self.get()
            else:
                logging.warning("forms.ProfileForm validation failed!, user %s" % user.nickname())
                return self.get(form=form)
        #}}}
        elif self.request.get('submit_static_edit'): #{{{3
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
            form = forms.ProfileForm(residence, locality_defined=True, formdata=self.request.POST)
            if form.validate():
                # всё правильно, заносим данные в хранилище
                if form.locality.data: # если был запрос на изменение места жительства
                    name, id, url = form.locality.data.rsplit(';', 2)
                    keyname = "id_%s" % id
                    R = Residence.get_or_insert(keyname, id=int(id), name=name, url=url)
                    # Если м.ж. поменялось и у прежнего м.ж. это единственный пользователь, удаляем
                    if R.key() != U.residence.key() and U.residence.users.count() < 2:
                        U.residence.delete()
                    # Обязательные поля
                    U.residence = R
                # Необязательные для заполнения поля
                for prop in ('name', 'surname', 'patronymic', 'gender'):
                    field = getattr(form, prop)
                    setattr(U, prop, field.data)
                if form.birthdate.data['year']: # данные по дате либо все, либо ни одной
                    b_data = form.birthdate.data
                    U.birthdate = date(int(b_data['year']), int(b_data['month']), int(b_data['day']))
                # Помещаем изменения в хранилище
                U.put()

                return self.get()
            else:
                return self.get(action="edit_static", form=form)
        #}}}
        elif self.request.get('delete_account'): #{{{3
            # Нажата кнопка "Удалить аккаунт"
            # Удаляем объект User и все относящиеся к нему объекты Prop, UserTrend и, возможно, Residence.
            # Модель CommonCityData (зависящую от Residence) не трогаем
            R = U.residence
            count = R.users.count()

            @db.transactional(xg=True)
            def txn():
                # удаляем все пользовательские данные
                db.delete(db.query_descendants(U))
                # если в данном месте проживает не более одного пользователя, то удаляем
                if count < 2:
                    R.delete()
                # И наконец удаляем сам аккаунт
                U.delete()

            txn()
            return self.get()
        #}}}
        elif self.request.get('delete_all_props'): #{{{3
            # Нажата кнопка "Удалить все параметры"
            # удаляются все объекты UserTrend и Prop, относящиеся к пользователю.
            # удаляем все пользовательские данные
            db.delete(db.query_descendants(U))
            return self.get()
        #}}}
        elif self.request.get('submitCommonProps'): #{{{3
            # Нажата кнопка "Сохранить" (submitCommonProps)
            # Изменяется свойство common_props профиля пользователя (models.User)
            form = forms.CommonProperties(self.request.POST)
            if form.validate(): # левые value у common_props не прокатят
                common_props = []
                common_props.extend(form.indiceProps.data)
                common_props.extend(form.commodityProps.data)
                common_props.extend(form.currencyProps.data)
                for data in form.astroProps.data:
                    common_props.extend((data+'_asc', data+'_dec', data+'_dis'))
                common_props.extend(form.geomagneticProps.data)
                common_props.extend(form.weatherProps.data)
                U.common_props = common_props
                U.put()
                return self.get()
            else:
                return self.get()
        #}}}
        elif self.request.get('delete_prop'): #{{{3
            # Нажата кнопка "Удалить параметр"
            # Удаляются записи из модели Prop (модель UserTrend не затрагивается).
            id = int(self.request.get('delete_prop'))
            P = Prop.get_by_id(id, parent=U) # подлог чужого id не пройдёт

            @db.transactional
            def txn():
                P.delete()

            @db.transactional
            def txn1():
                """Переупорядочиваем оставшиеся параметры.
                В одной транзакции параметр не успевает удалиться."""
                Ps = Prop.all().ancestor(U).order('order')
                newOrder = 1
                for P in Ps:
                    if P.order != newOrder:
                        P.order = newOrder
                        P.put()
                    newOrder += 1

            txn()
            txn1()
            return self.get()
        #}}}
        elif self.request.get('submit_add_prop'): #{{{3
            # Добавление параметра в хранилище
            form = forms.Add_prop(self.request.POST)
            if form.validate():
                @db.transactional
                def txn():
                    """Имена ключей у Prop не используются, так как любые свойства могут
                    впоследствии меняться. Для идентификации используются id.
                    """
                    # Больше U.propsLimit параметров нельзя (д. проверяться при валидации формы)
                    cPs = Prop.all().ancestor(U).count()
                    if cPs >= U.propsLimit:
                        logging.error("User's prop count equals propsLimit (%d == %d), user: %s."
                            " Check Add_prop form validation." % (cPs, U.propsLimit, U.nickname))
                        return
                    # Определяем порядок
                    order = Prop.all().ancestor(U).count() + 1
                    P = Prop(parent=U, name=form.name.data, type=form.type.data, order=order)
                    P.comment = form.comment.data
                    # Единицы измерения используется только с числовыми типами
                    if form.type.data in types_with_measure:
                        P.measure = form.measure.data
                    else:
                        P.measure = ""
                    # свойства шкалы используются только, если тип "Шкала"
                    if form.type.data == 'scale':
                        data = form.scale_attrs_field.data
                        P.scale_attrs = [data['scale_from'], data['scale_to'], data['scale_step']]
                    else:
                        P.scale_attrs = []
                    # сохраняем в хранилище
                    P.put()

                txn()
                return self.get()
            else:
                return self.get(action="add_prop", form=form)
        #}}}
        elif self.request.get('submit_edit_prop'): #{{{3
            # Занесение изменений обычного параметра в хранилище
            id = int(self.request.get('submit_edit_prop'))
            P = Prop.get_by_id(id, parent=U) # подлог чужого id не пройдёт
            form = forms.Edit_prop(P, self.request.POST)
            if form.validate():
                @db.transactional
                def txn():
                    # Если поменялся порядок, то переупорядочиваем все параметры
                    if P.order != form.order.data:
                        Ps = Prop.all().ancestor(U)
                        propsOrders = []
                        for p in Ps:
                            if p.key() == P.key():
                                propsOrders.append([p, form.order.data])
                            else:
                                propsOrders.append([p, p.order])
                        propsOrders.sort(key=lambda x:x[1])
                        newOrder = 1
                        for p, order in propsOrders:
                            if p.key() == P.key():
                                P.order = newOrder
                            else:
                                if order != newOrder:
                                    p.order = newOrder
                                    p.put()
                            newOrder += 1

                    # Редактируем объект Prop
                    P.name = form.name.data
                    P.comment = form.comment.data
                    # P.order назначается выше
                    change_type(P, form.type.data)
                    # единицы измерения используется только с числовыми типами
                    if form.type.data in types_with_measure:
                        P.measure = form.measure.data
                    else:
                        P.measure = ""
                    # свойства шкалы используются только, если тип "Шкала"
                    if form.type.data == 'scale':
                        data = form.scale_attrs_field.data
                        P.scale_attrs = [data['scale_from'], data['scale_to'], data['scale_step']]
                    else:
                        P.scale_attrs = []
                    # сохраняем в хранилище
                    P.put()

                txn()
                return self.get()
            else:
                return self.get(action="edit_prop", form=form)
        #}}}
    #}}}
#}}}
class GetRegions(webapp2.RequestHandler): #{{{1
    """Получить список регионов для выбранной страны."""
    def get(self): #{{{2
        lang = self.request.get('lang')
        country = self.request.get('country')
        if lang not in ('ru', 'en'):
            lang = 'ru'
        residence = build_residence(lang, country)
        form = forms.ProfileForm(residence, lang=lang)
        html = form.render_region()
        self.response.write(html)
    #}}}
#}}}
class GetDistricts(webapp2.RequestHandler): #{{{1
    """Получить список районов или населённых пунктов для выбранной страны и региона."""
    def get(self): #{{{2
        lang = self.request.get('lang')
        country = self.request.get('country')
        region = self.request.get('region')
        if lang not in ('ru', 'en'):
            lang = 'ru'
        residence = build_residence(lang, country, region)
        form = forms.ProfileForm(residence, lang=lang)
        if form.district.choices:
            html = form.render_district()
        else:
            html = form.render_locality()
        self.response.write(html)
    #}}}
#}}}
class GetLocalities(webapp2.RequestHandler): #{{{1
    """Получить список населённых пунктов для выбранной страны, региона и (если есть) района."""
    def get(self): #{{{2
        lang = self.request.get('lang')
        country = self.request.get('country')
        region = self.request.get('region')
        district = self.request.get('district')
        if lang not in ('ru', 'en'):
            lang = 'ru'
        residence = build_residence(lang, country, region, district)
        form = forms.ProfileForm(residence, lang=lang)
        html = form.render_locality()
        self.response.write(html)
    #}}}
#}}}
