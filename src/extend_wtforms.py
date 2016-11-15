#coding: utf-8
#Imports {{{1
from datetime import datetime
import logging

from wtforms.form import Form
from wtforms import validators, widgets
from wtforms.fields import *
from wtforms.fields import _unset_value     # class MyFormField
from wtforms.widgets.core import HTMLString, html_params, TextInput
from cgi import escape


#def unicode_or_none(value) {{{1
def unicode_or_none(value):
    if value:
        value = unicode(value)
    return value


#def bool_or_none(value) {{{1
def bool_or_none(value):
    """Возвращает булево, если value булево или 'True' или 'False', и None, если value другое"""
    if value in [True, 'True']:
        return True
    elif value in [False, 'False']:
        return False
    else:
        return None


#def mystrip(string="") {{{1
def mystrip(string=""):
    if string:
        if type(string) in (str, unicode):
            string = string.strip()
    return string


class Form(Form): #{{{1
    """Расширяем класс формы новыми методами."""
    def as_table(self):
        """Возвращает форму в виде совокупности <tr>, не включая теги <table>.
        Навеяно django.forms.Form.as_table"""
        html = ""
        for field in self:
            errorAttr = titleAttr = requiredStr = ''
            field_kwargs = {}
            if field.errors:
                errorAttr = ' class="error"'
            if field.description:
                if type(field.description) is dict:
                    field_kwargs = field.description
                    if 'title' in field.description:
                        titleAttr = u' title="%s"' % field.description['title']
                else:
                    titleAttr = u' title="%s"' % field.description
            if field.flags.required:
                requiredStr = '<span class="required">*</span>'

            if field.errors:
                html += '<tr><td colspan="2">'
                html += '<ul class="error">'
                for error in field.errors:
                    html += '<li>' + error + '</li>'
                html += '</ul>'
                html += '</td></tr>'

            html += "<tr%s%s>" % (errorAttr, titleAttr)

            html += "<td>%s:%s</td>" % (field.label(), requiredStr)
            html += "<td>" + field(**field_kwargs) + "</td>"
            html += "</tr>"

        return html


#class ButtonWidget(object) {{{1
class ButtonWidget(object):
    """Реализует тег <button>."""
    #def __call__(self, field, **kwargs) {{{2
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', field.button_type)
        kwargs.setdefault('value', field.value)
        return HTMLString(u'<button %s>%s</button>' % (html_params(name=field.short_name, **kwargs), escape(unicode(field.text))))


class DateInput(TextInput): #{{{1
    """Меняет TextInput, чтобы type = 'date' и value в формате '%Y-%m-%d'"""
    input_type = "date"


class MySelectField(SelectField): #{{{1
    """Добавляем опции allow_blank и blank_text по аналогии с wtforms.ext.appengine.fields.ReferencePropertyField."""
    def __init__(self, label=None, validators=None, coerce=unicode_or_none, choices=None, allow_blank=False, blank_text=u'', **kwargs): #{{{2
        super(MySelectField, self).__init__(label, validators, coerce, choices, **kwargs)
        self.allow_blank = allow_blank
        self.blank_text = blank_text

    def iter_choices(self): #{{{2
        if self.allow_blank:
            yield (u'__None', self.blank_text, self.data is None)
        # наследование генераторов не проходит, поэтому copy-paste
        for value, label in self.choices:
            # обход проблемы /wtforms/widgets/core.py:28 (html_params)
            if value is True:
                value = 'True'
            yield (value, label, self.coerce(value) == self.data)

    def process_formdata(self, valuelist): #{{{2
        if valuelist:
            if valuelist[0] == '__None':
                self.data = None
            else:
                try:
                    self.data = self.coerce(valuelist[0])
                except ValueError:
                    raise ValueError(self.gettext(u'Invalid Choice: could not coerce'))

    def pre_validate(self, form): #{{{2
        if not self.choices:    # поле типа SelectField не м.б. без опций, а наше может
            return              # управление передаётся функции validate()
        if not self.allow_blank or self.data is not None:
            super(MySelectField, self).pre_validate(form)


#class StripTextField(TextField) {{{1
class StripTextField(TextField):
    """По сравнению с TextField в начало списка фильтров добавляется фильтр mystrip"""
    #def __init__(self, *args, **kwargs) {{{2
    def __init__(self, *args, **kwargs):
        filters = list(kwargs.get('filters', tuple()))
        if mystrip not in filters:
            filters.insert(0, mystrip)
        super(StripTextField, self).__init__(filters=filters, *args, **kwargs)  


#class ButtonField(SubmitField) {{{1
class ButtonField(SubmitField):
    """Поле, реализуемое через тег <button>.
    Дополнительно добавляется атрибут text, button_type и при выводе поля необязательное значение value."""
    widget = ButtonWidget()

    #def __init__(self, label=None, validators=None, **kwargs) {{{2
    def __init__(self, label=None, validators=None, **kwargs):
        # Тип кнопки
        button_type = kwargs.pop('button_type', "submit")
        self.button_type = button_type
        # Текст на кнопке
        text = kwargs.pop('text', label or button_type.capitalize())    
        self.text = text
        # value
        value = kwargs.pop('value', text or label or button_type)
        self.value = value
        # Инициализация виджета
        super(ButtonField, self).__init__(label, validators, **kwargs)


class MultipleCheckboxField(SelectMultipleField): #{{{1
    """Такой же как SelectMultipleField, за исключением того, что представляется в виде списка чекбоксов
    Интерация по полю будет возвращать подполя, позволяя пользовательское представление включённых чекбоксов."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput() 


#class MyFormField(FormField) {{{1
class MyFormField(FormField):
    """Добавляем возможность кастомизации префикса"""
    #def __init__(self, form_class, label=None, validators=None, prefix=None, separator='-', **kwargs) {{{2
    def __init__(self, form_class, label=None, validators=None, prefix=None, separator='-', **kwargs):
        super(MyFormField, self).__init__(form_class, label, validators, separator, **kwargs)
        if prefix is None:
            prefix = self.name + self.separator # поведение родителя
        self.prefix = prefix

    #def process(self, formdata, data=_unset_value) {{{2
    def process(self, formdata, data=_unset_value):
        # Этот блок был скопирован с родителя
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
            self._obj = data
        # Этот блок был изменён 
        if isinstance(data, dict):
            self.form = self.form_class(formdata=formdata, prefix=self.prefix, **data)
        else:
            self.form = self.form_class(formdata=formdata, obj=data, prefix=self.prefix)


class MFDateField(DateField): #{{{1
    """Расширение класса поля DateField (wtforms/fields/core.py:DateField).
    1. Добавляется возможность вводить даты в форматах, отличных от format ('%Y-%m-%d').
    2. Меняется виджет на <input type='date'/>
    3. В случае, если дата пришла в формате, отличном от format,
       в виджет она уходит в формате format.
    """
    widget = DateInput()

    def __init__(self, label=None, validators=None, format='%Y-%m-%d', other_formats=(), **kwargs): #{{{2
        super(MFDateField, self).__init__(label, validators, format, **kwargs)
        self.other_formats = other_formats

    def process_formdata(self, valuelist): #{{{2
        if valuelist:
            date_str = u' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format).date()
            except ValueError:
                data = None
                for f in self.other_formats:
                    try:
                        data = datetime.strptime(date_str, f).date()
                        break
                    except ValueError:
                        continue
                if data is not None:
                    self.data = data
                    self.raw_data = [data.strftime(self.format)]
                else:
                    self.data = None
                    if not self.other_formats:
                        raise ValueError(u'Строка даты %s не соответствует формату %s либо '
                            u'несуществующая дата.' % (date_str, self.format))
                    else:
                        raise ValueError(u'Строка даты %s не соответствует ни формату `%s`, ни '
                            u'одному из форматов (%s), либо несуществующая дата.' %
                            (date_str, self.format, ', '.join(self.other_formats)))


