#coding: utf-8
#doc {{{1
""" 
Скачиваем с сайта http://www.timeanddate.com/ данные:
- по Солнцу: sunrise, sunset, daylength (day_duration);
- по Луне: moonrise, moonset, illum. (moon_illuminated).
Фазу Луны выводим из illum.
Данные скачиваются по месяцам.
Сохраняем все данные в файл в формате yaml.
Схема yaml:
{
    'id_\d+': {
        date: {
            'sunrise': value,
            'sunset': value,
            'day_duration': value,
            'moonrise': value,
            'moonset': value,
            'moon_phase': value,
            'moon_illuminated': value
        },
        ...
    },
    ...
}
"""
#}}}
#Imports {{{1
import lxml.html as LH
from datetime import date, time, timedelta
import yaml
import sys

#}}}
class MonthDate(object): #{{{
    """Эмуляция даты, состоящей только из года и месяца.
    Поддерживаются только необходимые в скрипте операции.
    """
    def __init__(self, year, month):
        D = date(year, month, 1)
        self.year = D.year
        self.month = D.month

    def __cmp__(self, other):
        return cmp(self.year*100+self.month, other.year*100+other.month)

    def __add__(self, n):
        """Прибавить n месяцев"""
        month = self.month + n - 1
        year = self.year + month//12
        month = month % 12 + 1
        return MonthDate(year, month)

    def __sub__(self, n):
        return self.__add__(-n)

    def __repr__(self):
        return 'MonthDate(%d, %d)' % (self.year, self.month)

    #}}}
def calc_moon_phase(moon_illuminated, prev_moon_illuminated): #{{{1
    if moon_illuminated is None:
        return None
    elif moon_illuminated <= 1.0:
        return u'Новолуние'
    elif moon_illuminated < 40.0:
        if moon_illuminated > prev_moon_illuminated:
            return u'Растущий серп'
        elif moon_illuminated < prev_moon_illuminated:
            return u'Убывающий серп'
    elif moon_illuminated <= 60.0:
        if moon_illuminated > prev_moon_illuminated:
            return u'Первая четверть'
        elif moon_illuminated < prev_moon_illuminated:
            return u'Последняя четверть'
    elif moon_illuminated < 99.0:
        if moon_illuminated > prev_moon_illuminated:
            return u'Растущая луна'
        elif moon_illuminated < prev_moon_illuminated:
            return u'Убывающая луна'
    else:
        return u'Полнолуние'

    #}}}
#Variables {{{1
URLS = {
    'saint-petersburg': {
        'sun': 'http://www.timeanddate.com/sun/russia/saint-peterburg',
        'moon': 'http://www.timeanddate.com/moon/russia/saint-peterburg'
    },
    'bangkok': {
        'sun': 'http://www.timeanddate.com/sun/thailand/bangkok',
        'moon': 'http://www.timeanddate.com/moon/thailand/bangkok'
    },
    'nashville': {
        'sun': 'http://www.timeanddate.com/sun/usa/nashville',
        'moon': 'http://www.timeanddate.com/moon/usa/nashville'
    }
}
MONTH_FROM = MonthDate(2014, 8)
MONTH_TO = MonthDate(2015, date.today().month)

DATA = {}

#}}}
#Парсинг и наполнение DATA {{{1
for city, urls in URLS.items():
    # Сначала выясняем освещённость Луны в последний день месяца, предшествующего MONTH_FROM
    prevMonth = MONTH_FROM - 1
    P = LH.parse('%s?month=%d&year=%d' % (urls['moon'], prevMonth.month, prevMonth.year)).getroot()
    table = P.get_element_by_id('tb-7dmn')
    tr = table.cssselect('tr[data-day]')[-1]
    td = tr.getchildren()[-1]
    prev_moon_illuminated = float(td.text.replace('%','').replace(',','.'))
    
    DATA[city] = {}
    curMonth = MONTH_FROM

    while curMonth <= MONTH_TO:
        year = curMonth.year
        month = curMonth.month
        # Скачиваем солнечные данные на данный месяц
        P = LH.parse('%s?month=%d&year=%d' % (urls['sun'], month, year)).getroot()
        table = P.get_element_by_id('as-monthsun')
        trs = table.cssselect('tr[data-day]')
        for tr in trs:
            Date = date(year, month, int(tr.get('data-day')))
            DATA[city][Date] = {}
            tds = tr.getchildren()
            sunrise = time(*map(int, tds[1].text.strip().split(':')))
            sunset = time(*map(int, tds[2].text.strip().split(':')))
            # day_duration нужно округлить
            day_duration = time(*map(int, tds[3].text.split(':')))

            DATA[city][Date]['sunrise'] = sunrise
            DATA[city][Date]['sunset'] = sunset
            DATA[city][Date]['day_duration'] = day_duration

        # Скачиваем лунные данные на данный месяц
        P = LH.parse('%s?month=%d&year=%d' % (urls['moon'], month, year)).getroot()
        table = P.get_element_by_id('tb-7dmn')
        trs = table.cssselect('tr[data-day]')
        for tr in trs:
            Date = date(year, month, int(tr.get('data-day')))
            tds = tr.getchildren()
            fullMoon = False

            firstTd = tds.pop(0)
            if 'Full Moon' in firstTd.get('title', ''):
                fullMoon = True

            moonrise = None
            moonset = None
            col = 0
            while col < 6:
                td = tds.pop(0)
                colspan = int(td.get('colspan', 1))
                if colspan > 1:
                    pass
                else:
                    text = td.text
                    if text:
                        title = td.get('title')
                        if 'Moon rises' in title:
                            moonrise = time(*map(int, text.split(':')))
                        elif 'Moon sets' in title:
                            moonset = time(*map(int, text.split(':')))
                        else:
                            print u"ОШИБКА! Непредвиденный title: url=%s, title=%s" % (P.base_url, title)
                            raise ValueError
                col += colspan
            if moonrise is None and moonset is None:
                print u"ОШИБКА! И moonrise и moonset равны None: url=%s" % P.base_url
                raise ValueError

            text = tds[-1].text
            if text == '-':
                if fullMoon is True:
                    moon_illuminated = 100.0
                else:
                    moon_illuminated = None
            else:
                moon_illuminated = float(text.replace('%','').replace(',','.'))

            moon_phase = calc_moon_phase(moon_illuminated, prev_moon_illuminated)

            prev_moon_illuminated = moon_illuminated

            DATA[city][Date]['moonrise'] = moonrise
            DATA[city][Date]['moonset'] = moonset
            DATA[city][Date]['moon_phase'] = moon_phase
            DATA[city][Date]['moon_illuminated'] = moon_illuminated

        curMonth += 1

    #}}}
# Пробегаем по DATA и интерполируем None в moon_illuminated и moon_phase {{{1
for city, dates in DATA.iteritems():
    for Date, values in dates.iteritems():
        if values['moon_illuminated'] is None:
            prev_moon_illuminated = DATA[city][Date-timedelta(days=1)]['moon_illuminated']
            next_moon_illuminated = DATA[city][Date+timedelta(days=1)]['moon_illuminated']
            moon_illuminated = (prev_moon_illuminated + next_moon_illuminated) / 2
            DATA[city][Date]['moon_illuminated'] = moon_illuminated
            DATA[city][Date]['moon_phase'] = calc_moon_phase(moon_illuminated, prev_moon_illuminated)
    #}}}
# Сохранение данных в файл {{{1
with open('../src/resources/sun_and_moon_data.yaml', 'w') as F:
    yaml.dump(DATA, F, allow_unicode=True)
    #}}}
