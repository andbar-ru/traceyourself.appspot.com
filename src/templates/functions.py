#!coding: utf-8

"""
В модуле находятся функции, предназначенные для обработки и вывода данных в html-шаблонах,
если обрабока непростая и коряво выглядит в виде mako-функций и блоков.
"""
#Imports {{{1
from wtforms.widgets import html_params
from datetime import date
import logging

# dummy gettext {{{1
_ = lambda x: x

#nav_items {{{1
# Пункты меню для панелей навигации
nav_items = [
    {"href":"/", "text":_(u'О проекте')},
    {"href":"/prof", "text":_(u'Настройки')},
    {"href":"/prof/fill_data", "text":_(u'Заполнение параметров')},
    {"href":"/analysis", "text":_(u'Анализ')},
    {"href":"/contacts", "text":_(u'Контакты')}
]

#def top_nav(context, route=None) {{{1
def top_nav(context, route=None):
    h_ = context['_'] # hidden _
    html = "<ul>\n"
    last = len(nav_items) - 1
    for i, item in enumerate(nav_items):
        classes = []
        if i==0:
            classes.append("first")
        elif i==last:
            classes.append("last")
        if route is not None and item['href'] == route:
            classes.append("active")
        if len(classes) == 0:
            klass = ''
        elif len(classes) == 1:
            klass = ' class="%s"' % classes[0]
        else:
            klass = ' class="'
            for cl in classes:
                klass += cl + " "
            klass = klass[:-1] + '"'
        html += ' <li%s><a href="%s">%s</a></li>\n' % (klass, item['href'], h_(item['text']))
    html += "</ul>\n"

    context.write(html)
    return ''


#def bottom_nav(context, route=None) {{{1
def bottom_nav(context, route=None):
    h_ = context['_'] # hidden _
    html = "<ul>\n"
    for item in nav_items:
        if route is not None and item['href'] == route:
            klass=' class="active"'
        else:
            klass = ''
        html += ' <li%s><a href="%s">%s</a></li>\n' % (klass, item['href'], h_(item['text']))
    html += '<div class="clear"></div>\n'
    html += "</ul>\n"

    context.write(html)
    return ''


#def render_field_errors(context, field, errors='ALL') {{{1
def render_field_errors(context, field, errors='ALL'):
    """Возвращает html-код представления ошибок.
    errors (list) - какие ошибки показывать, по умолчанию все.
    """
    if errors == 'ALL':
        errors = ['errors', 'errors_']
    html = ""
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

    context.write(html)
    return ''


#def render_field(context, field, wrapper_='div', field_wrapper_=None, delimiter_=' {{{1
def render_field(context, field, wrapper_='div', field_wrapper_=None, delimiter_=': ',
                 show_label_=True, label_first_=True, show_errors_=True, field_content=None,
                 wrapper_attrs='', **kwargs):
    """Возвращает html-код представления поля формы.
    context - служебный аргумент mako (как self)
    field - поле (набор полей) (объект wtforms.Field)
    Заканчиваются символом '_', чтобы в случае чего не конфликтовать с **kwargs;
    wrapper_ - Тег, в который оборачивается поле (набор полей) и метка (label);
    field_wrapper_ - Тег, в который оборачивается само поле без метки (набор полей);
    delimiter_ - Строка, которая разделяет label и поле.
    show_label_ - Показывать ли метку (label);
    label_first_ - Сначала метку, потом поле;
    show_errors_ - Не показывать ошибки в поле (выделение красным и красное предупреждение);
    field_content - готовый html-код поля (когда требуется специфическая обработка содержимого поля)
    wrapper_attrs - атрибуты тега-обёртки. Атрибуты class и title не допускаются.
    **kwargs - атрибуты, напрямую отправляемые в обработчик __call__ объекта field. 
    """
    html = ""
    if show_errors_ == True:
        html += render_field_errors(context, field)

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
    if wrapper_attrs:
        wrapper_attrs = ' ' + wrapper_attrs.strip()
    
    html += u'<%s%s%s%s>' % (wrapper_, error_attr, title_attr, wrapper_attrs)
    if show_label_ == True and label_first_:
        html += unicode(field.label)
        if field.flags.required:
            html += '<span class="required">*</span>'
        html += delimiter_
    if field_wrapper_ is not None:
        html += u'<%s>' % field_wrapper_
    if field_content is not None:
        html += field_content
    else:
        html += field(**kwargs)
    if field_wrapper_ is not None:
        html += u'</%s>' % field_wrapper_
    if show_label_ == True and not label_first_:
        html += delimiter_
        html += unicode(field.label)
        if field.flags.required:
            html += '<span class="required">*</span>'
    html += '</' + wrapper_ + '>'

    context.write(html)
    return ''


#def select_type(context, sField) {{{1
def select_type(context, sField):
    """Возвращает html-форматированную строку поля select с выбором типа параметра/элемента.
    context не используется, так как html нужно не вывести, а использовать как строку.
    """
    num_types = ('scale', 'int', 'float')
    html = u'<select id="%s" name="%s">' % (sField.id, sField.name)
    for option in sField:
        if sField.data in num_types:
            if option.data in num_types:
                html += option()
            else:
                html += option(disabled=True)
        else:
            if option.data == sField.data:
                html += option()
            else:
                html += option(disabled=True)
    html += '</select>'

    return html
