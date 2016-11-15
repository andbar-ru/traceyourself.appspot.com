#coding: utf-8
"""
Здесь находятся классы форм, используемые в приложении.
Для построения форм используется библиотека WTForms
"""
#Imports {{{1
from datetime import date, timedelta
from collections import OrderedDict
import os
import logging
import re
import json
# app engine
from google.appengine.api import users
#from webapp2_extras.i18n import lazy_gettext as _ #не работает из-за кэширования объекта i18n, поэтому:
from lib.functions import my_lazy_gettext as _
# wtforms
from wtforms import validators, widgets
from wtforms.fields import *
from wtforms.fields.html5 import *
from wtforms.form import Form
from wtforms.validators import ValidationError
from extend_wtforms import *
# проект
import models

#Global variables {{{1
today = date.today()


#def get_U() {{{1
def get_U():
    """Возвращает объект models.User текущего пользователя, если он есть."""
    user = users.get_current_user()
    if user:
        U = models.User.get_by_key_name(user.email())
        if U:
            return U
    return None

#all_types {{{1
all_types = [('scale', _(u'Шкала')),   # шкала от 0 до 10 (хранится как int)
             ('int', _(u'Целочисленный')),
             ('float', _(u'Число с плавающей запятой')),
             ('bool', _(u'Булево')),
             ('time', _(u'Время')),
            ]

#Economical properties {{{1
#indiceProperties {{{2
indiceProperties = [
    ('Indice.micex', _(u'ММВБ')),
    ('Indice.rts', _(u'РТС')),
    ('Indice.dow', _(u'Доу Джонс')),
    ('Indice.sap500', _(u'S&P 500')),
    ('Indice.ftse100', _(u'FTSE 100')),
    ('Indice.sse', _(u'SSE Composite'))
]

#commodityProperties {{{2
commodityProperties = [
    ('Commodity.oil', _(u'Нефть Brent')),
    ('Commodity.gold', _(u'Золото')),
    ('Commodity.silver', _(u'Серебро')),
    ('Commodity.aluminium', _(u'Алюминий')),
]

#currencyProperties {{{2
currencyProperties = [
    ('Currency.usd_rub', 'USD/RUB'),
    ('Currency.eur_rub', 'EUR/RUB'),
    ('Currency.eur_usd', 'EUR/USD'),
    ('Currency.gbp_usd', 'GBP/USD'),
    ('Currency.eur_gbp', 'EUR/GBP'),
    ('Currency.eur_jpy', 'EUR/JPY'),
    ('Currency.usd_jpy', 'USD/JPY')
]

#astroProperties {{{1
astroProperties = [
    ('AstroData.sun', _(u'Солнце')),
    ('AstroData.moon', _(u'Луна')),
    ('AstroData.mercury', _(u'Меркурий')),
    ('AstroData.venus', _(u'Венера')),
    ('AstroData.mars', _(u'Марс')),
    ('AstroData.jupiter', _(u'Юпитер')),
    ('AstroData.saturn', _(u'Сатурн')),
    ('AstroData.uranus', _(u'Уран')),
    ('AstroData.neptune', _(u'Нептун')),
    ('AstroData.pluto', _(u'Плутон'))
]
#geomagneticProperties {{{1
geomagneticProperties = [
    ('CommonData.solar_radio_flux', _(u'Поток радиоизлучения (λ=10.7см)')),
    ('CommonData.mean_planetary_A_index', _(u'Усреднённый планетарный A-индекс')),
    ('CommonData.mean_planetary_Kp_index', _(u'Усреднённый планетарный Kp-индекс'))
]
#weatherProperties {{{1
weatherProperties = [
    ('CommonCityData.temperature', _(u'Температура воздуха')),
    ('CommonCityData.cloud_cover', _(u'Облачность')),
    ('CommonCityData.precipitation', _(u'Осадки')),
    ('CommonCityData.pressure', _(u'Атмосферное давление')),
    ('CommonCityData.humidity', _(u'Относительная влажность воздуха')),
    ('CommonCityData.wind_velocity', _(u'Скорость ветра')),
    ('CommonCityData.wind_direction', _(u'Направление ветра')),
    ('CommonCityData.sunrise', _(u'Восход Солнца')),
    ('CommonCityData.sunset', _(u'Заход Солнца')),
    ('CommonCityData.day_duration', _(u'Продолжительность светового дня')),
    ('CommonCityData.moonrise', _(u'Восход Луны')),
    ('CommonCityData.moonset', _(u'Заход Луны')),
    ('CommonCityData.moon_phase', _(u'Фаза Луны')),
    ('CommonCityData.moon_illuminated', _(u'Освещённость Луны'))
]
#}}}
#def render_field_errors(field, errors='ALL') {{{1
def render_field_errors(field, errors='ALL'):
    """Возвращает html-код представления ошибок.
    errors (list) - какие ошибки показывать, по умолчанию все.
    """
    if errors == 'ALL':
        errors = ['errors', 'errors_']
    html = ''
    if hasattr(field, 'errors_') and 'errors_' in errors: # FormField errors
        html += '<ul class="error">'
        for error in field.errors_:
            html += '<li>' + error + '</li>'
        html += "</ul>"
    if field.errors and 'errors' in errors:               # Field errors
        html += '<ul class="error">'
        if type(field.errors) is dict:                    # Field in FormField
            for error_list in field.errors.values():
                for error in error_list:
                    html += '<li>' + error + '</li>'
        else:
            for error in field.errors:
                html += '<li>' + error + '</li>'
        html += '</ul>'

    return html
#}}}
def render_field(field, wrapper='div', fieldWrapper=None, delimiter=': ', showLabel=True, #{{{1
                 labelFirst=True, showErrors=True, fieldContent=None, wrapperAttrs='', **kwargs):
    """Возвращает html-код представления поля формы.
    field - поле (набор полей) (объект wtforms.Field)
    wrapper - Тег, в который оборачивается поле (набор полей) и метка (label);
    fieldWrapper - Тег, в который оборачивается само поле без метки (набор полей);
    delimiter - Строка, которая разделяет label и поле.
    showLabel - Показывать ли метку (label);
    labelFirst - Сначала метку, потом поле;
    showErrors - Не показывать ошибки в поле (выделение красным и красное предупреждение);
    fieldContent - готовый html-код поля (когда требуется специфическая обработка содержимого поля)
    wrapperAttrs - атрибуты тега-обёртки. Атрибуты class и title не допускаются.
    **kwargs - атрибуты, напрямую отправляемые в обработчик __call__ объекта field.
    """
    html = ''
    if showErrors == True:
        html += render_field_errors(field)

    # атрибут title
    title_attr = ''
    if field.description:
        if type(field.description) is dict:
            if 'title' in field.description:
                title_attr = u' title="%s"' % field.description['title']
        else:
            title_attr = u' title="%s"' % field.description
    # class="error" 
    if field.errors:
        error_attr = ' class="error"'
    else:
        error_attr = ''
    # wrapper attrs
    if wrapperAttrs:
        wrapperAttrs = ' ' + wrapperAttrs.strip()
    
    html += u'<%s%s%s%s>' % (wrapper, error_attr, title_attr, wrapperAttrs)
    if showLabel == True and labelFirst:
        html += unicode(field.label)
        if field.flags.required:
            html += '<span class="required">*</span>'
        html += delimiter
    if fieldWrapper is not None:
        html += u'<%s>' % fieldWrapper
    if fieldContent is not None:
        html += fieldContent
    else:
        html += field(**kwargs)
    if fieldWrapper is not None:
        html += u'</%s>' % fieldWrapper
    if showLabel == True and not labelFirst:
        html += delimiter
        html += unicode(field.label)
        if field.flags.required:
            html += '<span class="required">*</span>'
    html += '</' + wrapper + '>'

    return html
#}}}
def description_kwargs(field, keys=()): #{{{1
    kwargs = {}
    for key in keys:
      value = field.description.get(key)
      if value:
        kwargs[key] = value
    return kwargs
#}}}
#def validate_prop_uniqueness(form, field) {{{1
def validate_prop_uniqueness(form, field):
    """Название параметра должно быть уникальным для данного пользователя."""
    U = get_U()
    if not hasattr(form, 'current_prop_name') or form.current_prop_name != field.data:  # новое название или название редактировалось
        if models.Prop.all().ancestor(U).filter('name', field.data).get():
            raise ValidationError(_(u'У вас уже есть параметр с названием "%s"') % field.data)

#################
# Шаблоны полей #
#################
#def name_field() {{{1
# Название параметра или элемента
def name_field():
    """Возвращает поле названия параметра"""
    uniq_validator = validate_prop_uniqueness
    message = _(u'Название параметра может состоять только из букв, цифр, пробелов, символов тире и подчёркивания и должно начинаться с буквы')
    return StripTextField(
        _(u'Название'),
        [validators.InputRequired(message=_(u'Вы не указали название параметра')),
         validators.Regexp(r'^[^\W\d_][\w =)(,\.-]*$', re.U, message=message),
         uniq_validator],
        description=message
    )

#measure_field {{{1
# Единицы измерения
measure_field = StripTextField(
    _(u'Единица измерения'),
    description = _(u'Используется только с числовыми типами'))

#def choices(scale_attrs) {{{1
def choices(scale_attrs):
    """Возвращает набор радио-точек для шкалового параметра/элемента"""
    # направление шкалы и коэффициент
    if scale_attrs[2] > 0:
        k = 1
    else:
        k = -1
    choices = [(i,i) for i in range(scale_attrs[0], scale_attrs[1]+k, scale_attrs[2])]
    return choices

############################################
# Субформы (являются аргументом FormField) #
############################################
class DateForm(Form): #{{{1
    """Субформа, состоящая из 3 полей select для ввода пользователем даты."""
    day = MySelectField(_(u'День'), choices=[(str(i), i) for i in range(1,32)], allow_blank=True)
    month = MySelectField(_(u'Месяц'), choices=zip(map(str, range(1,13)), [_(u'января'),
        _(u'февраля'),_(u'марта'),_(u'апреля'),_(u'мая'),_(u'июня'),_(u'июля'),_(u'августа'),
        _(u'сентября'),_(u'октября'),_(u'ноября'),_(u'декабря')]), allow_blank=True)
    year = MySelectField(_(u'Год'), choices=[(str(i), i) for i in range(today.year-100,today.year+1)], allow_blank=True)

    def validate(self): #{{{2
        """Расширение наследованного метода. Дополнительно проверяется корректность даты."""
        super(DateForm, self).validate()
        # если проверка по отдельным полям прошла успешно, проверяем все поля в совокупности
        if not self.errors:
            None_count = self.data.values().count(None)
            # если не выбрано ни одного значения, дата будет пустой
            if None_count == 3:
                return True
            # если выбрано значение хотя бы у одного из полей, оно д.б. выбрано у всех
            elif None_count in (1,2):
                self.errors_ = []
                for key in self.data.keys():
                    if self.data[key] is None:
                        self.errors_.append(_(u'Вы не указали %s') % unicode(getattr(self, key).label).lower())
                return False
            # проверяем корректность даты
            year = int(self.data['year'])
            month = int(self.data['month'])
            day = int(self.data['day'])
            try:
                D = date(year, month, day)
            except ValueError:
                self.errors_ = [_(u'Неверная дата')]
                return False
            else:
                if D > date.today():
                    self.errors_ = [_(u'Дата находится в будущем')]
                    return False
                else:
                    return True
        else:
            return False
    #}}}
    def render(self): #{{{2
        html = render_field_errors(self, errors=['errors_'])
        for field in self:
            html += render_field(field, wrapper='span', showLabel=False) + ' '

        return html
    #}}}
#}}}
class LocationForm(Form): #{{{1
    """Субформа, предназначенная для выбора населённого пункта."""
    lang = HiddenField(_(u'Язык'), [validators.AnyOf(('ru','en'), message=_(u'Язык должен быть ru или en'))])
    country = SelectField(_(u'Страна')) # default in __init__
    region = MySelectField(_(u'Регион'), [validators.Optional()], default='ALL')
    district = MySelectField(_(u'Район'), [validators.Optional()], default='ALL')
    locality = MySelectField(_(u'Населённый пункт')) # validate_locality

    def __init__(self, residence=None, locality_defined=False, lang=None, **kwargs): #{{{2
        """Здесь заполняются опции для полей country, region, locality, и задаётся свойство lang.
        residence - объект населённого пункта со свойствами-(страна, регион и т.д.)
        locality_defined - если True, то поле необязательно для заполнения. Ошибки игнорируются.
        lang - язык географических названий.
        """
        # инициализация формы
        if lang != 'en': # в т.ч. None
            lang = 'ru'
        kwargs.setdefault('lang', lang)
        if lang == 'en':
            kwargs.setdefault('country', '179')
        else:
            kwargs.setdefault('country', '169')
        super(LocationForm, self).__init__(**kwargs)

        # проверять locality или нет? См. validate_locality
        if locality_defined:
            self.locality.description = 'defined'
        # действия, специфичные для этой формы
        with open('./rp5/%s/countries' % self.lang.data) as F:
            countries = json.load(F)
            self.country.choices = [(d,name) for name,d in countries.iteritems()]
            self.country.choices.sort(key=lambda t: t[1])
        with open('./rp5/%s/countries' % self.lang.data) as F:
            countries = json.load(F)
            self.country.choices = [(d,name) for name,d in countries.iteritems()]
            self.country.choices.sort(key=lambda t: t[1])
        if residence:
            self.country.process_data(residence.country)    # эта страна selected
            if hasattr(residence, 'regions'):
                self.region.choices = residence.regions
                if residence.all_regions is True:
                    self.region.choices.insert(0, ('ALL', _(u'Все регионы')))
                if hasattr(residence, 'region'):
                    self.region.process_data(residence.region) # этот регион selected
            if hasattr(residence, 'districts'):
                self.district.choices = residence.districts
                self.district.choices.insert(0, ('ALL', _(u'Все районы')))
                if hasattr(residence, 'district'):
                    self.district.process_data(residence.district)  # этот район selected
            if hasattr(residence, 'localities'):
                self.locality.choices = residence.localities
    #}}}
    def validate_locality(form, field): #{{{2
        """InputRequired только для незарегистрированного пользователя"""
        if field.description == 'defined':
            return validators.Optional()(form, field)
        else:
            return validators.InputRequired(message=_(u'Необходимо указать населённый пункт'))(form, field)
    #}}}
    def render(self, edit=True, withAnchor=False, **kwargs): #{{{2
        classname = self.__class__.__name__
        html = ''

        if classname == 'LocationForm':
            attrs = ''
            for k,v in kwargs.iteritems():
                if k == 'class_':
                    attrs += 'class="%s" ' % v
                else:
                    attrs += '%s="%s" ' % (k,v)
            if attrs:
                attrs = ' ' + attrs.rstrip()

            if withAnchor == True:
                html += '<a name="locationForm"></a>'

            html += '<form%s>' % attrs

        html += render_field(self.lang, showLabel=False)

        if classname != 'LocationForm' and edit == True:
            html += '<p class="note">%s</p>' % _(u'Выбрать другой населённый пункт:')

        html += '<div id="choose_locality">'
        html += '<table><tr>'
        html += self.render_country()
        if self.region.choices:
            html += self.render_region()
        if self.district.choices:
            html += self.render_district()
        # Ошибки нужно показывать независимо, отображается locality select или нет
        html += render_field_errors(self.locality)
        if self.locality.choices:
            html += self.render_locality()
        html += '</tr></table>'
        html += '</div>'

        if classname == 'LocationForm':
            html += '<input type="submit" name="submitLocationForm" value="%s"/>' % _(u'Сохранить')
            html += '<input type="reset" id="resetLocationForm" value="%s"/>' % _(u'Отмена')
            html += '</form>'

        return html
    #}}}
    def render_country(self): #{{{2
        fieldAttrs = {'size':12, 'data-initial':self.country.data}
        html = render_field(self.country, wrapper='td', delimiter='<br/>', **fieldAttrs)
        html += '<td style="vertical-align: middle"><input type="submit" id="get_regions" name="get_regions" value=">>>" title="%s"/></td>' % _(u'Показать регионы')
        return html
    #}}}
    def render_region(self): #{{{2
        fieldAttrs = {'size':12, 'data-initial':self.region.data}
        html = render_field(self.region, wrapper='td', delimiter='<br/>', **fieldAttrs)
        html += '<td style="vertical-align: middle"><input type="submit" id="get_districts" name="get_districts" value=">>>" title="%s"/></td>' % _(u'Показать районы')
        return html
    #}}}
    def render_district(self): #{{{2
        html = render_field(self.district, wrapper='td', delimiter='<br/>', size=12)
        html += '<td style="vertical-align: middle"><input type="submit" id="get_localities" name="get_localities" value=">>>" title="%s"/></td>' % _(u'Показать населённые пункты')
        return html
    #}}}
    def render_locality(self): #{{{2
        return render_field(self.locality, wrapper='td', delimiter='<br/>', showErrors=False, size=12)
    #}}}
#}}}
#class ScaleAttrs(Form) {{{1
class ScaleAttrs(Form):
    """Субформа, состоящая из 3 полей IntegerField
    для ввода свойств шкалы параметра/элемента с типом 'scale'
    """
    scale_from = IntegerField(_(u'от'), [validators.Optional()], default=0)
    scale_to = IntegerField(_(u'до'), [validators.Optional()], default=10)
    scale_step = IntegerField(_(u'шаг'), [validators.Optional()], default=1)

    #def validate(self) {{{2
    def validate(self):
        """Расширение наследованного метода.
        Дополнительно проверяется корректность свойств шкалы относительно друг друга:
        - При положительном scale_step: scale_from < scale_to.
        - При отрицательном scale_step: scale_from > scale_to.
        - scale_from и scale_to не м.б. равны.
        - scale_step не м.б. = 0.
        - количество градаций не д.б. больше 100.
        - (scale_to - scale_from) / scale_step д.б. натуральным числом
        """
        super(ScaleAttrs, self).validate()
        # если проверка по отдельным полям прошла успешно, проверяем все поля в совокупности
        if not self.errors:
            None_count = self.data.values().count(None)
            # если нет ни одного значения, пропустить
            if None_count == 3:
                return True
            # если есть значение хотя бы у одного из полей, значения д.б. у всех
            elif None_count in (1,2):
                self.errors_ = []
                for key in self.data.keys():
                    if self.data[key] is None:
                        self.errors_.append(_(u'Вы не указали `%s`') % unicode(getattr(self, key).label).lower())
                return False
            # проверяем корректность значений в совокупности
            scale_from = int(self.data['scale_from'])
            scale_to = int(self.data['scale_to'])
            scale_step = int(self.data['scale_step'])
            max_gradation_count = 100
            if scale_step > 0 and scale_from > scale_to:
                self.errors_ = [_(u'При положительном шаге "от" должен быть меньше "до"')]
                return False
            elif scale_step < 0 and scale_from < scale_to:
                self.errors_ = [_(u'При отрицательном шаге "от" должен быть больше "до"')]
                return False
            elif scale_from == scale_to:
                self.errors_ = [_(u'"от" и "до" не должны быть равны')]
                return False
            elif scale_step == 0:
                self.errors_ = [_(u'Шаг не должен равняться 0')]
                return False
            elif (scale_to - scale_from)/scale_step > max_gradation_count:
                gradation_count = (scale_to - scale_from)/scale_step
                self.errors_ = [_(u'Количество градаций в шкале не должно превышать %d, у вас %d: (%d-%d)/%d')
                    % (max_gradation_count, gradation_count, scale_to, scale_from, scale_step)]
                return False
            elif (scale_to - scale_from) % scale_step != 0:
                # догадываемся о том, каким д.б. scale_to
                excess = (scale_to - scale_from) % scale_step
                scale_to_0 = scale_to - excess
                scale_to_1 = scale_to_0 + scale_step
                self.errors_ = [_(u'Шаг должен помещаться в диапазон от %d до %d целое количество раз; предлагаемые значения "до": %d, %d')
                    % (scale_from, scale_to, scale_to_0, scale_to_1)]
                return False
            else:
                return True
        else:
            return False

#########
# Формы #
#########
#########################
# Формы по адресу /prof #
#########################
class ProfileForm(LocationForm): #{{{1
    """Форма, позволяющая пользователю занести свои статические данные (зарегистрироваться) на сайте,
    если пользователь отсутствует в модели User и редактировать свои данные, если профиль уже есть."""
    name = StripTextField(_(u'Имя'), [validators.Length(max=25, message=_(u'Слишком длинное имя'))])
    surname = StripTextField(_(u'Фамилия'), [validators.Length(max=25, message=_(u'Слишком длинная фамилия'))])
    patronymic = StripTextField(_(u'Отчество'), [validators.Length(max=25, message=_(u'Слишком длинное отчество'))])
    gender = MySelectField(_(u'Пол'), choices=[('M', _(u'М')),('F', _(u'Ж'))], allow_blank=True)
    birthdate = FormField(DateForm, label=_(u'Дата рождения'))

    def render(self, edit=False, locality=None, withAnchor=False, **kwargs): #{{{2
        attrs = ''
        for k,v in kwargs.iteritems():
            if k == 'class_':
                attrs += 'class="%s" ' % v
            else:
                attrs += '%s="%s" ' % (k,v)
        if attrs:
            attrs = ' ' + attrs.rstrip()

        html = ''

        if withAnchor == True:
            html += '<a name="edit_static"></a>'
        
        html += '<form%s>' % attrs
        if edit is False:
            html += '<p><strong>%s</strong></p>' % _(u'Заполнение личных данных')
        else:
            html += '<p><strong>%s</strong></p>' % _(u'Редактирование личных данных')
        html += render_field(self.name, maxlength=25)
        html += render_field(self.surname, maxlength=25)
        html += render_field(self.patronymic, maxlength=25)
        html += render_field(self.gender)
        html += '<div>%s:' % self.birthdate.label
        html += self.birthdate.render()
        html += '</div>'
        html += '<p>%s<span class="required">*</span> ' % _(u'Место пребывания')
        if locality is not None:
            html += locality
        html += '</p>'
        html += super(ProfileForm, self).render(edit)
        html += '<table width="100%">'
        html += '<tr>'
        name = 'submit_static_edit' if edit is True else 'submit_static'
        html += '<td align="left"><input type="submit" name="%s" value="%s"/></td>' % (name, _(u'Сохранить'))
        if edit is True:
            html += '<td align="right"><input class="dangerous" type="submit" name="delete_account" value="%s" onclick="%s"/></td>' % (_(u'Удалить аккаунт'), _(u'return confirm(\'Вы уверены? Все ваши данные и тренд будут удалены.\')'))
        html += '</tr>'
        html += '</table>'
        html += '<div>%s</div>' % _(u'Звёздочкой (<span class="required">*</span>) отмечены поля, обязательные для заполнения')
        html += '</form>'

        return html
    #}}}
#}}}
class CommonProperties(Form): #{{{1
    """Форма из флажков, позволяющая пользователю отметить общие параметры,
    которые он хочет учитывать при анализе"""
    indiceProps = MultipleCheckboxField(_(u'Индексы'), choices=indiceProperties)
    commodityProps = MultipleCheckboxField(_(u'Товары'), choices=commodityProperties)
    currencyProps = MultipleCheckboxField(_(u'Валютные пары'), choices=currencyProperties)
    astroProps = MultipleCheckboxField(_(u'Астрономические данные'), choices=astroProperties)
    geomagneticProps = MultipleCheckboxField(_(u'Геомагнитные данные'), choices=geomagneticProperties)
    weatherProps = MultipleCheckboxField(_(u'Данные погоды'), choices=weatherProperties)
    submitCommonProps = SubmitField(_(u'Сохранить'))

#class Add_prop(Form) {{{1
class Add_prop(Form):
    """Форма добавления обычного параметра."""
    name = name_field()
    comment = TextAreaField(
        _(u'Краткое описание'),
        [validators.Length(max=500, message=_(u'Слишком длинное описание (максимум 500 символов)'))]
    )
    type = SelectField(_(u'Тип'), choices=all_types, default='scale')
    measure = measure_field
    scale_attrs_field = FormField(
        ScaleAttrs,
        label=_(u'Свойства шкалы'),
        description=_(u'Используется только с типом "Шкала"'),
        widget=widgets.ListWidget('ul'))
    submit_add_prop = ButtonField(text=_(u'Добавить'), value="1")

# Служебные свойства используются в шаблонах и функциях валидации (выше)

#def Edit_prop(prop, formdata=None) {{{1
def Edit_prop(prop, formdata=None):
    """Форма редактирования параметра. Используется в /prof
    prop - объект models.Prop
    formdata - POST-данные формы"""
    orderDescription = _(u'Число, определяющее порядок следования параметров на страницах &#34;Настройки&#34;, &#34;Заполнение параметров&#34; и &#34;Анализ&#34;. Порядок начинается с 1. Все параметры переупорядочиваются каждый раз при изменении порядка у любого из параметров, поэтому в поле можно вводить дробное число (5.5), чтобы поместить параметр между двумя другими, а также отрицательные (-1) или заведомо большие числа (1000), чтобы сделать параметр первым или последним.')
    class F(Form):
        current_prop_name = prop.name  # служебное свойство
        # Поля
        name = name_field()
        comment = TextAreaField(
            _(u'Краткое описание'),
            [validators.Length(max=500, message=_(u'Слишком длинное описание (максимум 500 символов)'))]
        )
        type = SelectField(_(u'Тип'), choices=all_types, default='scale')
        order = FloatField(_(u'Порядок'), description=orderDescription)
        measure = measure_field
        # не scale_attrs, п.ч. надо показывать текущие значения, а тип list не подходит для этого
        scale_attrs_field = FormField(ScaleAttrs,
                                      label=_(u'Свойства шкалы'),
                                      description=_(u'Используется только с типом "Шкала"'),
                                      widget=widgets.ListWidget('ul'))
        submit_edit_prop = ButtonField(text=_(u'Сохранить'), value=prop.key().id())
        delete_prop = ButtonField(text=_(u'Удалить параметр'), value=prop.key().id())
    scale_attrs = prop.scale_attrs
    if scale_attrs != []:
        scale_attrs_field = {'scale_from':scale_attrs[0], 'scale_to':scale_attrs[1], 'scale_step':scale_attrs[2]}
    else:
        scale_attrs_field = {}
    return F(formdata=formdata, obj=prop, scale_attrs_field=scale_attrs_field)

###################################
# Формы по адресу /prof/fill_data #
###################################
def FillDataForm(U, props='ALL', Date=None, formdata=None): #{{{1
    """Форма, в которую пользователь вбивает данные своих параметров.
    Генерируется динамически на основе аргумента props (к.п. все параметры пользователя).
    U - объект User
    props - объект GqlQuery(models.Prop)
    Date - дата, за которую показывать/заносить значения
        Правила обработки даты, если Date==None:
            value: с JS: new Date(); без JS: date.today()
            max:   с JS: new Date(); без JS: date.today() + timedelta(days=1)
            Если new Date() отличается от date.today() больше, чем на ±сутки, то используется date.today()
    formdata - POST-данные формы"""
    kwargs = {} # здесь ищутся значения полей, если их нет в formdata, заполняется дальше
    UTCDate = date.today()
    DateIsToday = False
    if Date is None:
        Date = UTCDate
        DateIsToday = True

    if props == 'ALL':
        Ps = models.Prop.all().ancestor(U).order('order')

    class F(Form): #{{{2
        date = MFDateField(_(u'Дата'), [validators.InputRequired()], default=Date,
            other_formats=('%d.%m.%Y', '%d/%m/%Y'),
            description={'max':(UTCDate + timedelta(days=1)).isoformat()})
        UTCdate = HiddenField(default=UTCDate)
        isToday = HiddenField(default=DateIsToday)

        def validate_date(form, field): #{{{3
            """Дата в этой форме должна быть между 01.01.2012 и завтра (из-за часовых поясов)"""
            first_date = date(2012,1,1)
            last_date = date.today() + timedelta(days=1)
            Date = field.data
            if Date < first_date:
                raise ValidationError(_(u'Дата не может быть раньше 01.01.2012.'))
            elif Date > last_date:
                raise ValidationError(_(u'Дата не может быть позже сегодняшней.'))
            else:
                return
        #}}}
        def render(self, **kwargs): #{{{3
            attrs = ''
            for k,v in kwargs.iteritems():
                if k == 'class_':
                    attrs += 'class="%s" ' % v
                else:
                    attrs += '%s="%s" ' % (k,v)
            if attrs:
                attrs = ' ' + attrs.rstrip()
            
            html = '<form%s>' % attrs
            text = _(u'Дата вводится в формате "дд.мм.гггг" или "гггг-мм-дд".')
            html += '<p id="dates_hint" class="note">%s</p>' % text
            html += '<p>'
            html += render_field(self.date, wrapper='span', delimiter=':&nbsp;', min='2012-01-01',
                max=self.date.description['max'])
            html += unicode(self.UTCdate)
            html += unicode(self.isToday)
            text = _(u'Обновить значения параметров')
            html += '<input type="submit" id="update_data" name="update_data" value="%s"/>' % text
            html += '</p>'
            html += '<p><b>%s</b></p>' % _(u'Параметры:')
            html += '<ul>'
            for field in self:
                if field.name not in ('date', 'UTCdate', 'isToday'):
                    html += '<li>'
                    html += render_field(field, wrapper='span',
                        delimiter=': <span class="note">(%s)</span> ' % field.description['type'],
                        **description_kwargs(field, ["size", "class_"])) + ' '
                    html += field.description['measure']
                    html += '</li>'
            html += '</ul>'
            html += '<input type="submit" name="submit" value="%s"/>' % _(u'Занести значения')
            html += '</form>'

            return html
        #}}}
    #}}}

    for P in Ps:
        # Описание поля не в виде строки, а в виде словаря для повышения функционала
        description = {}

        # Описание поля
        description["type"] = P.type
        description["measure"] = P.measure if P.measure else ''
        if P.type in ('int', 'time'):
            description["size"] = 5
        elif P.type == 'float':
            description["size"] = 7
        # name и id поля
        name = "prop%d" % P.key().id()
        # значения полей по-умолчанию
        if not formdata:
            kwargs.setdefault(name, P.get_value(Date)) # значение за дату Date

        if P.type == 'scale':
            description['class_'] = "horiz_list"
            scale_attrs = P.scale_attrs
            setattr(F, name, RadioField(P.name, [validators.Optional()], coerce=int,
                    choices=choices(scale_attrs), description=description))
        elif P.type == 'bool':
            setattr(F, name, MySelectField(P.name, coerce=bool_or_none,
                    choices=[(True, _(u'Истина')),(False, _(u'Ложь'))], allow_blank=True,
                    description=description))
        elif P.type == 'int':
            setattr(F, name, IntegerField(P.name, [validators.Optional()],
                    description=description))
        elif P.type == 'float':
            setattr(F, name, FloatField(P.name, [validators.Optional()],
                    description=description))
        elif P.type == 'time':
            description["title"] = _(u'Время вводится в формате `ЧЧ:ММ`')
            setattr(F, name, DateTimeField(P.name, [validators.Optional()],
                    format="%H:%M", description=description))
        else:   # строковый
            # setattr(F, name, StripTextField(P.name, description=description))
            pass

    return F(formdata=formdata, **kwargs)
#}}}
class ContactForm(Form): #{{{1
    subject = StringField(
        _(u'Тема'),
        [validators.InputRequired(message=_(u'Вы не указали тему письма'))],
        description={'size':80}
    )
    message = TextAreaField(
        _(u'Сообщение'),
        [validators.InputRequired(message=_(u'Сообщение не может быть пустым'))],
        description={'rows':10, 'cols':50}
    )
    email = EmailField(
        _(u'Email для ответа'),
        [validators.Optional(), validators.Email(message=_(u'Неправильный email адрес'))],
        description={'title':_(u'Куда отправлять возможный ответ.'), 'size':50}
    )
    cc_myself = BooleanField(
        _(u'Копия (cc)'),
        description=_(u'Отправить копию письма на ваш email. Игнорируется, если вы не залогинены.')
    )
#}}}
class CommonDataForm(CommonProperties): #{{{1
    """Главная форма на странице /show_common_data"""
    residence = MySelectField(
        label=_(u'Населённый пункт'),
        choices=[(str(R.id), R.name) for R in models.Residence.all()],
        blank_text=_(u'Выберите населённый пункт'),
        allow_blank=True
    )
    dateFrom = MFDateField(_(u'с'), [validators.InputRequired(_(u'Вы не указали дату "с".'))])
    dateTo = MFDateField(_(u'по'), [validators.InputRequired(_(u'Вы не указали дату "по".'))])
    submit = SubmitField(_(u'Показать'))

    def validate_dateFrom(form, field):
        if field.data and form.dateTo.data:
            if field.data > form.dateTo.data:
                raise ValidationError(_(u'Дата "с" не может быть позднее даты "по".'))

    def validate_residence(form, field):
        if form.weatherProps.data and not field.data:
            raise ValidationError(_(u'Если вы выбрали данные погоды, то следует выбрать и населённый пункт.'))

    def validate_indiceProps(form, field):
        if not any((form.indiceProps.data, form.commodityProps.data, form.currencyProps.data,
                    form.astroProps.data, form.geomagneticProps.data, form.weatherProps.data)):
            raise ValidationError(_(u'Нужно выбрать хотя бы один показатель.'))
#}}}
