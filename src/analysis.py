#coding: utf-8
# imports {{{1
from os import path
import logging
import csv
import xlsxwriter
import StringIO
import lxml.html as lxhtml
from datetime import date, datetime
import re
# app engine
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import Key
# Шаблонизатор mako
from mako. template import Template
from mako.lookup import TemplateLookup
TEMPLATES_DIR = path.join(path.dirname(__file__), 'templates')
lookup = TemplateLookup(
    directories=[TEMPLATES_DIR],
    input_encoding="utf-8",
    format_exceptions=True,
)
# проект
from models import *
from lib.functions import get_i18n

#Global variables {{{1
#rgxNums {{{2
rgxNums = re.compile(r'\d+')
#rgxYesNo {{{2
rgxYesNo = re.compile(u'\(Да\)|\(Нет\)', re.U)


#def format4xlsx(content, type_) {{{1
def format4xlsx(content, type_):
    """Преобразовывает значение (из строки) для записи его в файл xlsx."""
    if type_ == 'date':
        content = datetime.strptime(content, '%d.%m.%Y').date()
    if type_ == 'time':
        try:
            content = datetime.strptime(content, '%H:%M').time()
        except ValueError: # пустая ячейка
            pass
    if type_ == 'duration':
        try:
            nums = rgxNums.findall(content)
            content = float(nums[0]) + float(nums[1])/60
        except IndexError: # пустая ячейка
            pass
    elif type_ == 'bool':
        if content == u'Да':
            content = 1
        elif content == u'Нет':
            content = 0
        else:
            pass
    elif type_ == 'int' or type_ == 'scale':
        try:
            content = int(content)
        except ValueError: # пустая ячейка
            pass
    elif type_ == 'float' or type_ == 'circ':
        try:
            content = float(content)
        except ValueError: # пустая ячейка
            pass
    else:
        pass

    return content


class Analysis(webapp2.RequestHandler): #{{{1
    """Выбрать тип анализа."""
    #def get(self) {{{2
    def get(self):
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
        if user:
            logout_url = users.create_logout_url(self.request.uri)
        else:
            logout_url = users.create_login_url(self.request.uri)

        # Формирование и представление шаблона
        template_values = {
            '_': _,
            'lang': lang,
            'animation': animation,
            'user': user,
            'logout_url': logout_url,
            'route': '/analysis'
        }
        template = lookup.get_template("analysis.mako")
        self.response.write(template.render(**template_values))
    #}}}
#}}}
class AnalysisSaved(webapp2.RequestHandler): #{{{1
    """Элементы анализа по данным пользователя"""
    #def __init__(self, *args, **kwargs) {{{2
    def __init__(self, *args, **kwargs):
        super(AnalysisSaved, self).__init__(*args, **kwargs)
        self.WARNINGS = []

    #def get(self, user=None) {{{2
    def get(self, user=None):
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

        # определяем юзера, по умолчанию текущий
        if user is None:
            user = users.get_current_user()
        else:
            if '@' not in user:
                user += '@gmail.com'
            user = users.User(user)

        if user:    # пользователь залогинен или определён
            # Проверить, есть ли данный пользователь в нашем хранилище
            U = User.get_by_key_name(user.email())
            # ссылка для разлогинивания
            logout_url = users.create_logout_url(self.request.uri)

            # Если пользователь зарегистрирован
            if U:
                # Анализ выполняется по ajax-запросу после загрузки страницы

                # Данные шаблона
                template_values = {
                    '_': _,
                    'lang': lang,
                    'animation': animation,
                    'user': user, # login.mako
                    'logout_url': logout_url, # login.mako
                    'route': '/analysis',
                }

                # Формирование и представление шаблона
                template = lookup.get_template("analysis_saved.mako")
                self.response.write(template.render(**template_values))

            # Если пользователь не зарегистрирован
            else: # if U
                self.redirect("/prof")

        # Пользователь не залогинен
        else:
            return self.redirect(users.create_login_url(self.request.uri))

    # def post(self) {{{2
    def post(self):
        """Создание файла и передача его пользователю"""
        if self.request.get('submit') != 'table2file':
            return None
        
        # Заголовки и парсинг {{{3
        # Формат файла
        fileFormat = self.request.get('format').encode('utf-8')
        # С какой таблицей работаем
        tableId = self.request.get('tableId').encode('utf-8')
        if tableId == 'dataTable':
            tag = 'td'
        else:
            tag = 'th'
        # Заголовки файла
        if fileFormat == 'csv':
            contentType = 'text/csv'
        elif fileFormat == 'xlsx':
            contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        self.response.headers['Content-Type'] = contentType
        self.response.headers['Content-Disposition'] = 'attachment;filename=%s-%s.%s' % (tableId, date.today().strftime('%Y%m%d'), fileFormat)
        # parse html
        content = self.request.get('content')
        table = lxhtml.fromstring(content)

        # if fileFormat == 'csv' {{{3
        if fileFormat == 'csv':
            # csv
            writer = csv.writer(self.response, delimiter=';')
            # Строка заголовков
            # Так как csv не поддерживает rowspan, colspan то в заголовке оставляем только названия параметров
            thead = table.find('thead')
            headers = thead.xpath('//%s[@data-csvheader]' % tag)
            headers.sort(key=lambda h:int(h.get('data-csvorder')))
            header_row = [h.get('data-csvheader').encode('utf-8') for h in headers]
            writer.writerow(header_row)
            # Строки с данными
            tbody = table.find('tbody')
            for tr in tbody:
                row = [td.text.encode('utf-8') for td in tr]
                writer.writerow(row)

        # if fileFormat == 'xlsx' {{{3
        elif fileFormat == 'xlsx':
            output = StringIO.StringIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory':True})
            worksheet = workbook.add_worksheet()
            worksheet.freeze_panes(5, 1)

            # formats {{{4
            def add_format(ps={}):
                """Join default format and props and return resulting format."""
                props = {'font_name':'Arial', 'font_size':8, 'text_wrap':1, 'border':1}
                props.update(ps)
                return workbook.add_format(props)

            format0 = add_format({'font_color':'gray'})
            format_name = add_format({'bold':1, 'valign':'top'})
            format_thead = add_format({'bold':1, 'align':'center', 'valign':'vcenter'})
            format_date = add_format({'num_format':'dd.mm.yyyy'})
            format_time = add_format({'num_format':'hh:mm'})
            format_float2 = add_format({'num_format':'0.00'})
            format_corr = add_format({'num_format':'0.00', 'align':'center', 'valign':'vcenter', 'font_color':'gray'})
            format_corrDiagonal = add_format({'fg_color':'gray'})
            format_corrVeryhigh = add_format({'num_format':'0.00', 'align':'center', 'valign':'vcenter', 'font_color':'red', 'bold':1})
            format_corrHigh = add_format({'num_format':'0.00', 'align':'center', 'valign':'vcenter', 'bold':1})
            format_corrSignificant = add_format({'num_format':'0.00', 'align':'center', 'valign':'vcenter'})
            format_corrMedium = add_format({'num_format':'0.00', 'align':'center', 'valign':'vcenter', 'underline':1})
            format_nameool = add_format({'num_format':'BOOLEAN'})
            format_number = add_format()

            # preparation {{{4
            thead = table.find('thead')
            rowsN = len(thead)
            tr = thead.cssselect('tr.colnumbers')[0]
            colsN = len(tr)
            types = [th.get('data-type') for th in tr]

            widths = [float(w)/7.6 for w in self.request.get('widths').split(',')]
            for col,width in enumerate(widths):
                worksheet.set_column(col, col, width)

            def set_height(h):
                h = float(h) / 1.9
                if h < 15:
                    h = 15
                return h

            heights = [set_height(h) for h in self.request.get('heights').split(',')]
            for row,height in enumerate(heights):
                worksheet.set_row(row, height)

            grid = [] # rows x cols
            for r in range(rowsN):
                grid.append([])
                for c in range(colsN):
                    grid[r].append(0)

            # table header {{{4
            row = 0
            for tr in thead:
                for th in tr:
                    # ячейка, в которую записываем значение или с которой начинается
                    # объединение = (row, col). Надо искать каждый раз.
                    col = grid[row].index(0)
                    try:
                        rowspan = int(th.get('rowspan'))
                    except TypeError, ValueError:
                        rowspan = 1
                    try:
                        colspan = int(th.get('colspan'))
                    except TypeError, ValueError:
                        colspan = 1
                    if rowspan==1 and colspan==1:
                        worksheet.write(row, col, th.text_content(), format_thead)
                        grid[row][col] = 1 # помечаем ячейку как заполненную
                    else: # объединение ячеек
                        row2 = row + rowspan - 1
                        col2 = col + colspan - 1
                        worksheet.merge_range(row, col, row2, col2, th.text_content(), format_thead)
                        # помечаем ячейки как заполненные
                        for r in range(row, row2+1):
                            for c in range(col, col2+1):
                                grid[r][c] = 1
                row += 1

            # table body {{{4
            tbody = table.find('tbody')
            for row, tr in enumerate(tbody):
                for col, td in enumerate(tr):
                    content = td.text_content().strip()
                    format = format0
                    type_ = types[col]

                    if tableId == 'dataTable':
                        content = format4xlsx(content, type_)
                        if type_ == 'date':
                            format = format_date
                        elif type_ == 'time':
                            format = format_time
                        elif type_ == 'duration':
                            format = format_float2
                        elif type_ == 'bool':
                            format = format_nameool
                        elif type_ in ('circ','circ_cat','int','scale','float'):
                            format = format_number
                    elif tableId == 'statTable':
                        if type_ == 'name':
                            format = format_name
                        elif row == 0: # Количество значений
                            content = format4xlsx(content, 'int')
                            format = format_number
                        elif row == 3: # Среднее значение
                            if type_ == 'bool': # '0.53 (Да)', '0.49 (Нет)'
                                content = rgxYesNo.sub('', content)
                                content = format4xlsx(content, 'float')
                                format = format_float2
                            elif type_ == 'time':
                                content = format4xlsx(content, 'time')
                                format = format_time
                            else:
                                content = format4xlsx(content, 'float')
                                format = format_float2
                        elif row == 4: # Стандартное отклонение
                            if type_ == 'time':
                                format = format_number
                            else:
                                content = format4xlsx(content, 'float')
                                format = format_float2
                        else:
                            content = format4xlsx(content, type_)
                            if type_ == 'time':
                                format = format_time
                            elif type_ == 'duration':
                                format = format_float2
                            elif type_ == 'bool':
                                format = format_nameool
                            elif type_ in ('circ','circ_cat','int','scale','float'):
                                format = format_number
                    elif tableId == 'corrTable':
                        if type_ == 'name':
                            format = format_name
                        else:
                            tdClass = td.get('class')
                            if tdClass is None:
                                format = format_corr
                            elif tdClass == 'diagonal':
                                format = format_corrDiagonal
                            elif tdClass == 'very_high':
                                format = format_corrVeryhigh
                            elif tdClass == 'high':
                                format = format_corrHigh
                            elif tdClass == 'significant':
                                format = format_corrSignificant
                            elif tdClass == 'medium':
                                format = format_corrMedium

                            content = format4xlsx(content, 'float')

                    if content == '':
                        content = ' '
                    worksheet.write(row+rowsN, col, content, format)

            workbook.close()

            output.seek(0)
            self.response.write(output.read())


class AnalysisTest(webapp2.RequestHandler): #{{{1
    """Элементы анализа по тестовым данным, закачанным пользователем."""
    #def get(self) {{{2
    def get(self):
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
        if user:
            logout_url = users.create_logout_url(self.request.uri)
        else:
            logout_url = users.create_login_url(self.request.uri)

        # Формирование и представление шаблона
        template_values = {
            '_': _,
            'lang': lang,
            'animation': animation,
            'user': user,
            'logout_url': logout_url,
            'route': '/analysis'
        }
        template = lookup.get_template("analysis_test.mako")
        self.response.write(template.render(**template_values))
