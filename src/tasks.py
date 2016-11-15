#coding: utf-8
# Imports {{{1
import webapp2
from google.appengine.ext import db
from google.appengine.api import urlfetch, logservice, mail
from google.appengine.api.urlfetch_errors import DownloadError, DeadlineExceededError
import urllib

from datetime import datetime, date, timedelta
import lxml.html as lxhtml
import re
import time
from time import time as Time
import logging

from models import *
from lib.functions import summary_value


#class GetSolarData(webapp2.RequestHandler) {{{1
class GetSolarData(webapp2.RequestHandler):
    SOLAR_SITE = "http://www.tesis.lebedev.ru/en/magnetic_storms.html"

    #def get(self) {{{2
    def get(self):
        T1 = Time()
        try:
            P = urlfetch.fetch(self.SOLAR_SITE, deadline=30)
        except DownloadError:
            logging.error("Could not fetch %s" % self.SOLAR_SITE)
            exit()
        else:   # Загрузка прошла успешно
            logging.info("SOLAR_SITE fetched at %d:%d" % (datetime.now().hour, datetime.now().minute))
            root = lxhtml.fromstring(P.content)
            table = root.find('.//table[@class="day_2 magn"]')
            date = table.find('.//h3').text.strip()
            date = datetime.strptime(date, "%B %d, %Y").date()
            date_str = date.isoformat()
            h2 = table.xpath('.//h2[@class="yellow"]')[-1]
            strongs = h2.xpath('following-sibling::strong')[:3]
            solar_radio_flux = mean_planetary_A_index = mean_planetary_Kp_index = None
            try:
                solar_radio_flux = int(strongs[0].text)
                mean_planetary_A_index = int(strongs[1].text)
                mean_planetary_Kp_index = int(strongs[2].text.split()[0])
            except TypeError:  # что-то осталось None
                logging.warning("There aren't values on %s" % self.SOLAR_SITE)
                pass            # значение останется пустым
            else:
                logging.info("""SOLAR_SITE data:
                                date: %s
                                solar_radio_flux: %d
                                mean_planetary_A_index: %d
                                mean_planetary_Kp_index: %d""" % (date_str, solar_radio_flux, mean_planetary_A_index, mean_planetary_Kp_index))

            common_data = CommonData.get_by_key_name(date_str)
            if common_data:
                logging.debug("there already was common data for %s" % date_str)
                common_data.solar_radio_flux = solar_radio_flux
                common_data.mean_planetary_A_index = mean_planetary_A_index
                common_data.mean_planetary_Kp_index = mean_planetary_Kp_index
            else:
                logging.debug("there wasn't common data for %s" % date_str)
                common_data = CommonData(key_name = date_str)
                common_data.date = date
                common_data.solar_radio_flux = solar_radio_flux
                common_data.mean_planetary_A_index = mean_planetary_A_index
                common_data.mean_planetary_Kp_index = mean_planetary_Kp_index
            try:
                common_data.put()
            except:
                logging.error("Could not put SOLAR data to the datastore")

        T2 = Time()
        logging.info("Длительность сбора геомагнитных данных: %.2f сек." % (T2-T1))
        self.response.write("It has been taken %.2f sec." % (T2-T1))


#def Urlfetch(url, **kwargs) {{{1
def Urlfetch(url, **kwargs):
    """Повторяющаяся операция скачивания страницы из интернета"""
    P = urlfetch.fetch(url, **kwargs)
    if P.status_code == 200:
        return P
    else:
        raise DownloadError


class RP5(webapp2.RequestHandler): #{{{1

    def get(self): #{{{2
        """Получить прогноз погоды по всем населённым пунктам модели Residence
        и положить результаты в модель CommonCityData.
        Прогноз собирается только за полные дни (с данными за все 4 отметки времени),
        т.е. в большинстве случаев начиная с завтрашних суток.
        Прогнозные данные агрегируются для полных суток, без разбива по отметкам времени.
        Страницы достаются с помощью сервиса urlfetch и парсятся с помощью lxml.html.parse
        Возможные проблемы:
        1. Страницы с прогнозом для данного id не существует:
            загрузится страница по редиректу, надо проверить id в P.final_url"""
        # Переменные
        T1 = Time()

        Rs = Residence.all()
        daysForward = 3 # сколько дней вперёд нас интересует
        tdOffset = 1 # количество ячеек, которое надо пропустить вначале каждой строки
        # Регулярки
        onmouseoverRe = re.compile(r"^tooltip\( this , '([^']+)' , 'hint' \)$")
        cloudinessRes = {
            'ru': re.compile(ur'''^<b>[\w ]+</b><br/>
                ((\(облаков\ нет\))|
                 (\(облака\ (вертикального\ развития\ (?P<vert>\d+)%(,\ )?)?
                            (нижнего\ яруса\ (?P<low>\d+)%(,\ )?)?
                            (среднего\ яруса\ (?P<mid>\d+)%(,\ )?)?
                            (верхнего\ яруса\ (?P<high>\d+)%(,\ )?)?
                  \)
                 )
                )$''', re.U|re.X),
            'en': re.compile(ur'''^<b>[\w ]+</b><br/>
                ((\(no\ clouds\))|
                 (\((clouds\ with\ vertical\ development\ (?P<vert>\d+)%(,\ )?)?
                    (low-level\ clouds\ (?P<low>\d+)%(,\ )?)?
                    (mid-level\ clouds\ (?P<mid>\d+)%(,\ )?)?
                    (high-level\ clouds\ (?P<high>\d+)%(,\ )?)?
                  \)
                 )
                )$''', re.U|re.X)
        }
        precipitationRes = {
            'ru': re.compile(ur'''^
                Явления\ погоды\ отсутствуют|Без\ осадков|
                (Преимущественно\ без\ осадков|(((Очень\ )?Сильный\ )?Ливневый|Обложной)\ (дождь|снег))
                \ \((?P<precipitation>[\d.]+)\ (мм\ воды|см\ снега)\ /\ 6\ часов\)$''', re.U|re.X|re.I),
            'en': re.compile(ur'''^
                No\ significant\ weather\ phenomena|Without\ precipitation|
                (Mainly\ without\ precipitation|((Very\ )?Heavy\ )?Rain\ Shower|Continuous\ (rain|snow))
                \ \((?P<precipitation>[\d.]+)\ (mm\ of\ water|cm\ of\ snow)\ /\ 6\ hours\)$''', re.U|re.X|re.I)
        }
        # обновлять ли существующие записи CCD
        update = True if self.request.get('update') == '1' else False

        def td_groups(tr, handleFirstDay): #{{{3
            """Функция возвращает группы ячеек, где первая группа - это первый день, вторая - следующий и т.д.
            Работает только со строками с параметрами и первая ячейка должна быть заголовком.
            tr - строка, ячейки из которой нужно вернуть;
            handleFirstDay - включать первый день или нет
            """
            tds = tr.getchildren()[tdOffset:]
            tdGroups = []
            curTdGroup = None
            firstDay = True

            while tds:
                td = tds.pop(0)
                if {'n','d','wd','wn','grayLittled','grayLittlen'} & set(td.get('class').split()): # новые сутки
                    if curTdGroup is not None:
                        if firstDay:
                            if handleFirstDay:
                                tdGroups.append(curTdGroup)
                            firstDay = False
                        else:
                            tdGroups.append(curTdGroup)
                    if (handleFirstDay and len(tdGroups) == daysForward+1) or (not handleFirstDay and len(tdGroups) == daysForward):
                        break
                    curTdGroup = []
                curTdGroup.append(td)
            else:
                # Если выход произошёл по причине окончания td, то что-то пошло не так
                raise UserWarning(u"Error: While loop has terminated through exhaustion of tds.")

            return tdGroups
            
        #}}}
        for R in Rs:
            # Неизменяемые переменные
            url = R.url
            lang = url[-2:]
            # Изменяемые переменные
            WEATHER_INFO = {} # Составной словарь
            days = []
            handleFirstDay = None # Обрабатывать первый день? Да, если полный.

            # Получение страницы с прогнозом
            try:
                P = Urlfetch(url, deadline=30)
            except DownloadError:
                logging.error(u"Не скачалась страница %s" % url)
                continue    # следующее место жительства
            except DeadlineExceededError:   # см. параметр deadline в fetch
                logging.error(u"Истекло время ожидания при скачивании страницы %s" % url)
                # В этот раз информацию по этому населённому пункту брать не будем
                continue    # следующее место жительства
            # страница скачалась без ошибок
            root = lxhtml.fromstring(P.content)
            try:
                # наличие этой таблицы критично
                forecastTable = root.find('.//table[@id="forecastTable"]')
                trs = forecastTable.getchildren()
            except AttributeError:
                logging.error(u"На странице %s нет таблицы с id=forecastTable" % url)
                continue    # следующее место жительства

            # Анализ таблицы с прогнозом
            # Если возникают ошибки, значит в таблице что-то поменялось
            # и нужно пересматривать весь анализ
            try:
                # Первая строка - даты
                # На основе её определяются ячейки, которые мы обрабатываем
                tr = trs[0]
                tds = tr.getchildren()
                firstDayTd = tds[tdOffset]
                nextDayTd = tds[tdOffset+1]
                firstDayColspan = int(firstDayTd.get('colspan'))
                fullDayColspan = int(nextDayTd.get('colspan'))
                # Сегодняшнее число населённого пункта может отличаться от сегодняшнего числа сервера,
                # но не больше, чем на 1
                today = date.today()
                firstDayText = firstDayTd.find('.//span[@class="monthDay"]').text
                if lang == 'ru':
                    firstDayNumber = int(firstDayText.split()[0]) # 28 октября
                elif lang == 'en':
                    firstDayNumber = int(firstDayText.split()[1].replace('.', '')) # October 28
                if firstDayNumber == today.day:
                    firstDay = today
                else:
                    diff = firstDayNumber - today.day
                    if abs(diff) == 1:  # месяц одинаковый
                        firstDay = today + timedelta(days=diff)
                    else:               # месяц разный
                        if diff > 0:    # локальный месяц - предыдущий (последнее число)
                            if today.month == 1:    # также меняется год на предыдущий (31.12)
                                firstDay = date(today.year-1, 12, firstDayNumber)
                            else:
                                firstDay = date(today.year, today.month-1, firstDayNumber)
                        else:           # локальный месяц - следующий (первое число)
                            if today.month == 12:   # также меняется год на следующий (01.01)
                                firstDay = date(today.year+1, 1, firstDayNumber)
                            else:
                                firstDay = date(today.year, today.month+1, firstDayNumber)
                # Если первый день представлен всеми временными отметки, то включаем его в результат
                if firstDayColspan == fullDayColspan:
                    WEATHER_INFO[firstDay] = {}
                    days.append(firstDay)
                    handleFirstDay = True
                else:
                    handleFirstDay = False

                for i in range(daysForward):
                    day = firstDay + timedelta(days=i+1)
                    WEATHER_INFO[day] = {}
                    days.append(day)

                # Обработка (выборочная) остальных строк
                for tr in trs[1:]:
                    title = tr[0].text_content()

                    # Облачность: 4 ячейки в полном дне
                    if u'Облачность' in title or 'Cloudiness' in title:
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            values = []
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                # информация хранится в атрибуте "onmouseover" дива:
                                onmouseover = td.find('./div/div').get('onmouseover')
                                tooltip = onmouseoverRe.match(onmouseover).group(1)
                                match = cloudinessRes[lang].match(tooltip)
                                if not match:
                                    logging.error(u'Несоответствие регулярному выражению в ячейке с облачностью: tooltip="%s"' % tooltip)
                                    raise ValueError
                                # Облачность определяем как максимальное из облачности всех уровней, кроме верхнего.
                                vert = int(match.group('vert') or 0)
                                low = int(match.group('low') or 0)
                                mid = int(match.group('mid') or 0)
                                value = max(vert,low,mid)
                                values.append(value)
                            cloud_cover = summary_value(values, "int")
                            WEATHER_INFO[day]['cloud_cover'] = cloud_cover

                    # Осадки: 8 ячеек в полном дне
                    elif u'Явления погоды' in title or 'Weather phenomena' in title:
                        # Т.к. данные по осадкам даются за 6 часов, то учитываем только чётные ячейки (сумма по чётным ячейкам д.б. итогу за день).
                        # Если значения осадков даются для снега, то теперь они даются в см (но рассматриваем это как мм).
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            values = []
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                onmouseover = td.find('./div').get('onmouseover')
                                tooltip = onmouseoverRe.match(onmouseover).group(1)
                                match = precipitationRes[lang].match(tooltip)
                                if not match:
                                    logging.error(u'Несоответствие регулярному выражению в ячейке с явлениями погоды: tooltip="%s"' % tooltip)
                                    raise ValueError
                                value = float(match.group('precipitation') or 0)
                                values.append(value/2.0) # делим на 2, потому осадки приводятся за 6 часов, а ячейки каждые 3 часа
                            precipitation = round(summary_value(values, "float_accumulative"), 1)
                            WEATHER_INFO[day]['precipitation'] = precipitation

                    # Температура: 4 ячейки в полном дне
                    elif u'Температура' in title or 'Temperature' in title:
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            values = []
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                value = int(td.find('div').text_content())
                                values.append(value)
                            temperature = summary_value(values, "int")
                            WEATHER_INFO[day]['temperature'] = temperature

                    # Давление: 4 ячейки в полном дне
                    elif u'Давление' in title or 'Pressure' in title:
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            values = []
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                value = int(td.find('div').text_content())
                                values.append(value)
                            pressure = summary_value(values, "int")
                            WEATHER_INFO[day]['pressure'] = pressure

                    # Влажность: 4 ячейки в полном дне
                    elif u'Влажность' in title or 'Humidity' in title:
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            values = []
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                value = int(td.text_content())
                                values.append(value)
                            humidity = summary_value(values, "int")
                            WEATHER_INFO[day]['humidity'] = humidity

                    # Скорость ветра: 4 ячейки в полном дне
                    elif u'Ветер: скорость' in title or 'Wind: speed' in title:
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            values = []
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                # если штиль, то тега div нет
                                div = td.find('div')
                                if div is not None:
                                    value = int(div.text)
                                else:
                                    value = int(td.text)
                                values.append(value)
                            wind_velocity = summary_value(values, "int")
                            WEATHER_INFO[day]['wind_velocity'] = wind_velocity

                    # Направление ветра: 4 ячейки в полном дне (8 направлений и штиль)
                    elif u'направление, румбы' in title or 'direction, compass points' in title:
                        if lang == 'ru':
                            direction_map = {u'С-В':'NE', u'В':'E', u'Ю-В':'SE', u'Ю':'S', u'Ю-З':'SW', u'З':'W', u'С-З':'NW', u'С':'N', u'ШТЛ':'C'}
                        elif lang == 'en':
                            direction_map = {'NE':'NE', 'E':'E', 'SE':'SE', 'S':'S', 'SW':'SW', 'W':'W', 'NW':'NW', 'N':'N', 'calm':'C'}
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            values = []
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                text = td.text_content()
                                value = direction_map[text]
                                values.append(value)
                            wind_direction = summary_value(values, "str")
                            WEATHER_INFO[day]['wind_direction'] = wind_direction

                    # Восход и заход солнца: 4 ячейки в полном дне
                    # ячейки могут быть пустыми (в данный период не было ни восхода, ни захода)
                    # восход в редких случаях может происходить ПОЗЖЕ захода (например 21 мая в Норильске)
                    # восхода и/или захода в конкретные сутки может вообще не быть
                    elif u'Солнце' in title or 'Sun' in title:
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            sunrise = None
                            sunset = None
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                text = td.text
                                if not text or text.find(':') == -1:    # время не указано
                                    pass
                                else:
                                    T = datetime.strptime(td.text, "%H:%M").time()
                                    if 'litegrey' in td.get('class').split():   # заход
                                        sunset = T
                                    else:
                                        sunrise = T
                            WEATHER_INFO[day]['sunrise'] = sunrise
                            WEATHER_INFO[day]['sunset'] = sunset

                    # Восход и заход луны: 4 ячейки в полном дне (см. примечания к солнцу)
                    elif u'Луна' in title or 'Moon' in title:
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            moonrise = None
                            moonset = None
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                text = td.text
                                if not text or text.find(':') == -1:    # время не указано
                                    pass
                                else:
                                    T = datetime.strptime(td.text, "%H:%M").time()
                                    if 'litegrey' in td.get('class').split():   # заход
                                        moonset = T
                                    else:
                                        moonrise = T
                            WEATHER_INFO[day]['moonrise'] = moonrise
                            WEATHER_INFO[day]['moonset'] = moonset

                    # Фаза и освещённость луны: 1 ячейка
                    elif u'фаза' in title or 'phase' in title:
                        phase_map = {
                            'New moon': u'Новолуние',
                            'Waxing crescent moon': u'Растущий серп',
                            'First quarter moon': u'Первая четверть',
                            'Waxing gibbous moon': u'Растущая луна',
                            'Full moon': u'Полнолуние',
                            'Waning gibbous moon': u'Убывающая луна',
                            'Last quarter moon': u'Последняя четверть',
                            'Waning crescent moon': u'Убывающий серп'
                        }
                        tdgroups = td_groups(tr, handleFirstDay)
                        for i,day in enumerate(days):
                            tdgroup = tdgroups[i]
                            for td in tdgroup:
                                div = td.find('div')
                                # информация хранится в атрибуте "onmouseover" дива, напр:
                                # onmouseover="tooltip( this , 'Убывающий серп, в полночь будет освещено 15%' , 'hint' )"
                                onmouseover = div.get('onmouseover')
                                phrase = onmouseover.split("'")[1]
                                moon_phase = phrase.split(',')[0]
                                if lang == 'en':
                                    moon_phase = phase_map[moon_phase]
                                moon_illuminated = int(re.search(r'(\d+)%', phrase, re.U).group(1))
                            WEATHER_INFO[day]['moon_phase'] = moon_phase
                            WEATHER_INFO[day]['moon_illuminated'] = moon_illuminated

            except (AttributeError, TypeError, ValueError):
                import sys
                logging.error(u"Ошибка парсинга таблицы с прогнозом: url=%s, exception: %s: %s (lineno: %d)" %
                    (url, sys.exc_info()[0].__name__, sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
                continue

            # Словарь с данными сформирован, заносим их в хранилище
            for day,data in WEATHER_INFO.iteritems():
                # Проверка, что все данные нашлись
                propsNotFound = []
                for prop in ('cloud_cover','precipitation','temperature','pressure','wind_velocity',
                             'wind_direction','humidity','sunrise','sunset','moonrise','moonset',
                             'moon_phase','moon_illuminated'):
                    if prop not in data:
                        propsNotFound.append(prop)

                if propsNotFound:
                    logging.error(u"Ошибка: в таблице не найдены показатели %s (url=%s)" %
                        (propsNotFound, url))
                    continue
                
                keyname = "%s-%s" % (R.key().name(), day.strftime("%Y%m%d"))
                CCD = CommonCityData.get_by_key_name(keyname)
                if not CCD or update is True:
                    CCD = CommonCityData(key_name=keyname)
                    # эти параметры не меняются
                    CCD.date = day
                    CCD.residence = R
                    CCD.users = [U.key().name() for U in R.users]
                    CCD.from_archive = False
                    CCD.sunrise = data['sunrise']
                    CCD.sunset = data['sunset']
                    CCD.moonrise = data['moonrise']
                    CCD.moonset = data['moonset']
                    CCD.moon_phase = data['moon_phase']
                    CCD.moon_illuminated = data['moon_illuminated']
                    # Вычисляем продолжительность светового дня
                    if data['sunrise'] and data['sunset']:  # норма
                        sunrise = datetime.strptime(data['sunrise'].isoformat(), "%H:%M:%S")
                        sunset = datetime.strptime(data['sunset'].isoformat(), "%H:%M:%S")
                        # В исключительно редких случаях восход может произойти ПОЗЖЕ захода (21 мая в Норильске)
                        if sunrise > sunset:
                            sunset = sunset.replace(hour=0, minute=0) + timedelta(days=1)   # 24:00 тех же суток (захода не было)
                        delta = sunset - sunrise
                        CCD.day_duration = datetime.strptime(str(delta), "%H:%M:%S").time()
                    else:
                        # На этапе тестирования выводим ошибки
                        logging.error("sunrise == None or sunset == None, keyname=%s" % keyname)
                        if not data['sunrise'] and not data['sunset']:  # полярный день или полярная ночь
                            # день или ночь определяем по последней доступной записи
                            prev_CCD = CommonCityData.gql("WHERE residence = :1 and date < :2 ORDER BY date DESC", R, day).fetch(1)
                            if not prev_CCD or not prev_CCD.day_duration:
                                # можно посчитать номер дня в году (%j) и, предполагая, что это северное полушарие,
                                # вычислить: 0 или 24 часа
                                logging.error("Нельзя вычислить продолжительность светового дня, нет данных, keyname = %s" % keyname)
                                day_of_year = int(day.strftime("%j"))
                                if 81 < day_of_year < 266:
                                    CCD.day_duration = time(23, 59, 59) # не получается time(24)
                                else:
                                    CCD.day_duration = time(0)
                            else:
                                if prev_day_duration.hour > 12:
                                    CCD.day_duration = time(23, 59, 59)
                                else:
                                    CCD.day_duration = time(0)
                        elif data['sunrise'] and not data['sunset']:    # первые сутки полярного дня
                            sunrise = datetime.strptime(data['sunrise'].isoformat(), "%H:%M:%S")
                            sunset = data['sunrise'].replace(hour=0, minute=0) + timedelta(days=1)  # 24:00 тех же суток (захода не было)
                            delta = sunset - sunrise
                            CCD.day_duration = datetime.strptime(str(delta), "%H:%M:%S").time()
                        elif not sunrise and sunset:    # последние сутки полярного дня либо пункт обрабатывается первый раз
                            sunset = datetime.strptime(data['sunset'].isoformat(), "%H:%M:%S")
                            sunrise = data['sunset'].replace(hour=0, minute=0)  # 00:00 тех же суток (восхода не было)
                            delta = sunset - sunrise
                            CCD.day_duration = datetime.strptime(str(delta), "%H:%M:%S").time()
                        else:   # недопустимый вариант
                            raise Exception

                # Выдать ошибку, если day_duration будет равняться None
                if CCD.day_duration == None:
                    logging.error("day_duration == None, keyname=%s" % keyname)

                # Остальные данные могут поменяться в любое время, поэтому перезаписываем
                CCD.temperature = data['temperature']
                CCD.cloud_cover = data['cloud_cover']
                CCD.precipitation = data['precipitation']
                CCD.pressure = data['pressure']
                CCD.humidity = data['humidity']
                CCD.wind_velocity = data['wind_velocity']
                CCD.wind_direction = data['wind_direction']

                CCD.put()
        T2 = Time()
        logging.info("Длительность сбора прогноза: %.2f сек." % (T2-T1))
        self.response.write("It has been taken %.2f sec." % (T2-T1))


class RP5Archive(webapp2.RequestHandler): #{{{1
    def get(self): #{{{2
        """Получить архив погоды за предыдущие сутки по всем населённым пунктам модели Residence, а
        также попытаться получить все пропущенные архивы, и положить результаты в модель
        CommonCityData, заменив ими прогнозные данные на ту же дату.
        Страницы достаются с помощью сервиса urlfetch и парсятся с помощью lxml.html.parse.
        Скачивать страницу желательно где-то позже 23 часов, чтобы избежать закачки текущих суток
        для какого-нибудь пункта с большой разницей в часовых поясах.
        Если в GET-параметрах указан day, то закачиваются данные на дату day.
        day даётся в формате %Y%m%d, например 20121115
        Возможные проблемы:
        * Страницы с прогнозом для данного id не существует:
          загрузится страница по редиректу, надо проверить id в P.final_url;
        * Не скачалась страница с архивом (DownloadError):
          занести пункт и дату в модель CommonCityDataMissed, чтобы попытаться их скачать позже.
        """
        #props_map {{{3
        # Соответствие названий параметров в таблице и словаре
        props_map = {
            'T':   'temperature',
            'Po':  'pressure',
            'U':   'humidity',
            'DD':  'wind_direction',
            'Ff':  'wind_velocity',
            'N':   'cloud_cover',
            'RRR': 'precipitation'
        }
        #}}}
        #wind_direction_map {{{3
        # Соответствие русских и английских названий румбов
        wind_direction_map_ru = {
            u'Ветер, дующий с северо-северо-востока':  'NNE',
            u'Ветер, дующий с северо-востока':         'NE',
            u'Ветер, дующий с востоко-северо-востока': 'ENE',
            u'Ветер, дующий с востока':                'E',
            u'Ветер, дующий с востоко-юго-востока':    'ESE',
            u'Ветер, дующий с юго-востока':            'SE',
            u'Ветер, дующий с юго-юго-востока':        'SSE',
            u'Ветер, дующий с юга':                    'S',
            u'Ветер, дующий с юго-юго-запада':         'SSW',
            u'Ветер, дующий с юго-запада':             'SW',
            u'Ветер, дующий с западо-юго-запада':      'WSW',
            u'Ветер, дующий с запада':                 'W',
            u'Ветер, дующий с западо-северо-запада':   'WNW',
            u'Ветер, дующий с северо-запада':          'NW',
            u'Ветер, дующий с северо-северо-запада':   'NNW',
            u'Ветер, дующий с севера':                 'N',
            u'Штиль, безветрие':                       'C'
        }
        # Соответствие английских и английских названий румбов
        wind_direction_map_en = {
            u'Wind blowing from the north-northeast': 'NNE',
            u'Wind blowing from the north-east':      'NE',
            u'Wind blowing from the east-northeast':  'ENE',
            u'Wind blowing from the east':            'E',
            u'Wind blowing from the east-southeast':  'ESE',
            u'Wind blowing from the south-east':      'SE',
            u'Wind blowing from the south-southeast': 'SSE',
            u'Wind blowing from the south':           'S',
            u'Wind blowing from the south-southwest': 'SSW',
            u'Wind blowing from the south-west':      'SW',
            u'Wind blowing from the west-southwest':  'WSW',
            u'Wind blowing from the west':            'W',
            u'Wind blowing from the west-northwest':  'WNW',
            u'Wind blowing from the north-west':      'NW',
            u'Wind blowing from the north-northwest': 'NNW',
            u'Wind blowing from the north':           'N',
            u'Calm, no wind':                         'C'
        }
        #}}}
        def put_to_ccdm(R, day): # {{{3
            """Заводит новую запись в CommonCityDataMissed на пункт R и дату day, если такой записи нет"""
            keyname = "%s-%s" % (R.key().name(), day.strftime('%Y%m%d'))
            CCDM = CommonCityDataMissed.get_by_key_name(keyname)
            if CCDM is None:
                CCDM = CommonCityDataMissed(key_name=keyname, date=day, residence=R)
                CCDM.put()
        #}}}
        def fetch_archive(R, day): # {{{3
            """Скачать архив погоды по пункту R на дату day"""
            # Соответствие параметров и их индексов в таблице
            # По обработке страницы их количество д.б. len(props_map)
            lang = R.url[-2:]
            props_indexes = {}
            # Значения параметров
            props_values = {
                'temperature': [],
                'pressure': [],
                'humidity': [],
                'wind_direction': [],
                'wind_velocity': [],
                'cloud_cover': [],
                'precipitation': [],
            }

            archive_url = R.archive_url # страница с архивом
            if not archive_url: # скачивание архива в первый раз
                url = R.url
                try:
                    P = Urlfetch(url, deadline=30)
                except DownloadError:
                    logging.error(u"Не скачалась страница %s" % url)
                    put_to_ccdm(R, day)
                    return False
                except DeadlineExceededError:   # см. параметр deadline в fetch
                    logging.error(u"Истекло время ожидания при скачивании страницы %s" % url)
                    put_to_ccdm(R, day)
                    return False
                # страница скачалась
                root = lxhtml.fromstring(P.content)
                try:
                    # Наличие этого элемента критично
                    xpath = './/div[@class="leftNavi"]//span[@class="verticalCenter"][1]/a'
                    archive_link = root.find(xpath)
                    archive_url = archive_link.get('href')
                except AttributeError:
                    logging.error(u"На странице %s нет элемента с xpath %s. Архив не скачиваем." % (url, xpath))
                    put_to_ccdm(R, day)
                    return False
                else:
                    # Чтобы больше не повторять выяснение адреса страницы с архивом
                    R.archive_url = archive_url
                    R.put()

            # страница, с которой скачивается архив
            POST = {
                "ed0": day.day,     # день
                "ed1": day.month,   # месяц
                "ed2": day.year,    # год
                "lang": "ru",
                "pe":  1            # ?
            }
            payload = urllib.urlencode(POST)
            try:
                P = Urlfetch(archive_url, payload=payload, method=urlfetch.POST, deadline=30)
            except DownloadError:
                logging.error(u"Не скачалась страница %s" % archive_url)
                put_to_ccdm(R, day)
                return False
            except DeadlineExceededError:   # см. параметр deadline в fetch
                logging.error(u"Истекло время ожидания при скачивании страницы %s" % archive_url)
                put_to_ccdm(R, day)
                return False
            if P.final_url and P.final_url != archive_url:
                logging.error(u"Страница с архивом погоды куда-то подевалась (%s)" % archive_url)
                put_to_ccdm(R, day)
                return False

            # Всё в поряде, обрабатываем страницу
            root = lxhtml.fromstring(P.content)
            try:
                # наличие этой таблицы критично
                archiveTable = root.find('.//table[@id="archiveTable"]')
                trs = archiveTable.getchildren() # здесь д.б. только tr
            except AttributeError:
                logging.error(u"На странице %s нет таблицы с id=archiveTable" % archive_url)
                put_to_ccdm(R, day)
                return False

            # Впоследствии идёт анализ таблицы с архивом
            # Если возникают ошибки, значит в таблице что-то поменялось
            # и нужно пересматривать весь анализ
            try:
                # Первая строка - параметры
                tr = trs[0]
                for i,td in enumerate(tr):
                    text = td.text_content()
                    if text in props_map:
                        props_indexes[props_map[text]] = i
                # Проверка количества параметров
                if len(props_indexes) < len(props_map):
                    logging.error(u"Обнаружены не все параметры, недостаёт: %s" %
                        ", ".join(set(props_map.values())-set(props_indexes)))

                # Остальные строки (д.б. 8, но м.б. 24 (Москва)) - значения параметров за различные отметки времени
                # - строка с заголовками (уже обработана выше);
                # - 8 строк (в норме) со сроками нужной даты (обрабатываем ниже);
                # - строка с последним сроком предыдущей даты (не трогаем).
                if len(trs) > 10:
                    logging.warning(u"Количество строк в таблице архива больше 10 (%s): дата=%s, url=%s"
                        % (len(trs), day.strftime("%d.%m.%Y"), archive_url))

                # По значению атрибута rowspan ячейки с датой определяем, сколько строк обработать
                rowspan = int(trs[1][0].get('rowspan'))

                if rowspan < 8: # есть не все строки
                    logging.warning(u"есть данные только по %d срокам: дата=%s, url=%s" %
                        (rowspan, day.strftime("%d.%m.%Y"), archive_url))
                elif rowspan > 8: # количество сроков больше ожидаемого
                    logging.warning(u"%d сроков, больше положенного: дата=%s, url=%s" %
                        (rowspan, day.strftime("%d.%m.%Y"), archive_url))

                for tr in trs[1:rowspan+1]:
                    if tr[0].get('rowspan') is not None: # первая строка
                        td_offset = 1
                    else:
                        td_offset = 0

                    hour = tr[td_offset].text_content()

                    for prop, i in props_indexes.iteritems():
                        td = tr[i+td_offset]
                        # информация содержится, как правило, в теге div.
                        # Если div'а нет или его содержимое '&nbsp;' ('\xa0'), то данные отсутствуют
                        div = td.find('div')
                        if div is not None and div.text != u"\xa0":
                            if prop == 'temperature':
                                value = float(div.text)
                            elif prop == 'pressure':
                                value = float(div.text)
                            elif prop == 'humidity':
                                value = int(div.text)
                            # ячейка с направлением ветра без div'а (обрабатывается ниже)
                            elif prop == 'wind_velocity':
                                # div.text: " (3 м/сек)"
                                value = int(re.search(r'\((\d+).*\)', div.text, re.U).group(1))
                            elif prop == 'cloud_cover':
                                if div.text==u'Облаков нет.' or div.text=='no clouds':
                                    value = 0
                                else:
                                    spans = div.findall('span[@class="dfs"]')
                                    if len(spans) == 2:     # ex: 70 – 80%.
                                        value = (int(spans[0].text) + int(spans[1].text)) / 2
                                    elif len(spans) == 1:   # ex: 100%.
                                        value = int(spans[0].text)
                                    elif len(spans) == 0:
                                        text1 = u"Небо не видно из-за тумана и/или других метеорологических явлений."
                                        text2 = 'Sky obscured by fog and/or other meteorological phenomena.'
                                        if div.text==text1 or div.text==text2:
                                            continue    # не учитываем
                                        # другой текст
                                        else:
                                            logging.error("len(spans) = 0, text: %s, url: %s" % (div.text, archive_url))
                                            continue
                                    else:
                                        logging.error("len(spans) > 2, url: %s" % archive_url)
                                        continue
                            elif prop == 'precipitation':
                                if div.text==u'Осадков нет' or div.text=='No precipitation':
                                    value = 0.0
                                # осадки были, но успели испариться
                                elif div.text==u'Следы осадков' or div.text=='Trace of precipitation':
                                    value = 0.1
                                else:
                                    value = float(div.text)
                            # добавляем значение в соответствующий набор значений
                            props_values[prop].append(value)
                        else:
                            if prop == 'wind_direction' and td.text != u"\xa0":
                                # направление ветра представлено без div'а, пример содержания <td>:
                                # "Ветер, дующий с северо-северо-востока"
                                if lang == 'ru':
                                    value = wind_direction_map_ru[td.text]
                                elif lang == 'en':
                                    value = wind_direction_map_en[td.text]
                                # добавляем значение в соответствующий набор значений
                                props_values[prop].append(value)
                            elif prop == 'precipitation':
                                # для осадков это нормальная ситуация
                                continue
                            else:
                                logging.warning(u"Нет значения по параметру `%s`, срок=%s, дата=%s, url=%s" %
                                    (prop, hour, day.strftime("%d.%m.%Y"), archive_url))
                                continue

                # Инициируем замену данных в хранилище
                keyname = "%s-%s" % (R.key().name(), day.strftime("%Y%m%d"))
                CCD = CommonCityData.get_by_key_name(keyname)
                if not CCD:
                    # такого быть не должно, только на localhost
                    # logging.error("There is not CommonCityData with keyname %s" % keyname)
                    CCD = CommonCityData(key_name=keyname, date=day, from_archive=True, residence=R)
                # Помечаем набор данных, как архив
                CCD.from_archive = True
                # Далее для каждого параметра вычисляем итоговое значение и записываем в хранилище
                for prop, values in props_values.iteritems():
                    # несмотря на то, что многие значения представлены типом float,
                    # реальная их итоговая точность -- int
                    if prop == 'temperature':
                        value = summary_value(values, 'int')
                    elif prop == 'pressure':
                        value = summary_value(values, 'int')
                    elif prop == 'humidity':
                        value = summary_value(values, 'int')
                    elif prop == 'wind_direction':
                        value = summary_value(values, 'str', reverse=True)
                    elif prop == 'wind_velocity':
                        value = summary_value(values, 'int')
                    elif prop == 'cloud_cover':
                        value = summary_value(values, 'int')
                    elif prop == 'precipitation':
                        if values == []:
                            value = 0.0     # д.б. float
                        else:
                            value = summary_value(values, 'float_accumulative')

                    setattr(CCD, prop, value)
                    # Остальные свойства остаются прежними
                CCD.put()
                return True

            # не перехваченные исключения
            except (AttributeError, ValueError):
                import sys
                logging.error("Ошибка парсинга таблицы с архивом: дата=%s, url=%s, exception: %s: %s (lineno: %d)" %
                    (day.strftime("%d.%m.%Y"), archive_url, sys.exc_info()[0].__name__, sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
                put_to_ccdm(R, day)
                return False
        #}}}


        T1 = Time()

        # Скачиваем архивы погоды за предыдущие сутки
        Rs = Residence.all()
        today = date.today()
        day = self.request.get('day')
        if not day:
            day = today - timedelta(days=1)
        else:
            day = datetime.strptime(day, "%Y%m%d").date()

        for R in Rs:
            fetch_archive(R, day)

        # Скачиваем пропущенные архивы, если есть
        CCDMs = CommonCityDataMissed.all()
        for CCDM in CCDMs:
            result = fetch_archive(CCDM.residence, CCDM.date)
            if result is True:
                CCDM.delete()

        T2 = Time()
        self.response.write("It has taken %.2f sec." % (T2-T1))
    #}}}
#}}}
class SaveRP5HTML(webapp2.RequestHandler): #{{{1
    def get(self): #{{{2
        """Сохранить html-страницы с прогнозом погоды по всем населённым пунктам модели Residence."""
        T1 = Time()
        Rs = Residence.all()

        for R in Rs:
            url = R.url
            try:
                P = Urlfetch(url, deadline=30)
            except DownloadError:
                logging.error(u"Не скачалась страница %s" % url)
                continue    # следующее место жительства
            except DeadlineExceededError:   # см. параметр deadline в fetch
                logging.error(u"Истекло время ожидания при скачивании страницы %s" % url)
                # В этот раз информацию по этому населённому пункту брать не будем
                continue    # следующее место жительства
            # страница скачалась без ошибок
            keyname = '%s-%s' % (R.key().name(), datetime.now().strftime('%Y%m%d'))
            CCDP = CommonCityDataPages(key_name=keyname, html=P.content.decode('utf-8'))
            CCDP.put()

        yearAgo = date.today() - timedelta(days=360)
        CCDPs = CommonCityDataPages.all().filter('date <', yearAgo)
        for CCDP in CCDPs:
            CCDPs.delete()

        T2 = Time()
        self.response.write("It has been taken %.2f sec." % (T2-T1))
    #}}}
#}}}
class GetEcData(webapp2.RequestHandler): #{{{1
    def get(self): #{{{2
        """Получить информация по российским и мировым фондовым индексам, товарам и валютным парам.
        Цепляем первую строку с данными из таблицы и пофиг, что за дата.
        """
        T0 = Time()
        today = date.today()
        groups = {
            'Indice': {'model':Indice, 'entities':{}},
            'Commodity': {'model':Commodity, 'entities':{}},
            'Currency': {'model':Currency, 'entities':{}}
        }
        dateRE = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
        timeRE = re.compile(r'^\d{2}:\d{2}$')

        props = {
            # индексы
            'micex': ('Indice', 'http://stocks.investfunds.ru/indicators/view/216/'),
            'rts': ('Indice', 'http://stocks.investfunds.ru/indicators/view/218/'),
            'dow': ('Indice', 'http://stocks.investfunds.ru/indicators/view/221/'),
            'sap500': ('Indice', 'http://stocks.investfunds.ru/indicators/view/222/'),
            'ftse100': ('Indice', 'http://stocks.investfunds.ru/indicators/view/223/'),
            'sse': ('Indice', 'http://stocks.investfunds.ru/indicators/view/263/'),
            # товары
            'oil': ('Commodity', 'http://stocks.investfunds.ru/indicators/view/624/'),
            'gold': ('Commodity', 'http://stocks.investfunds.ru/indicators/view/224/'),
            'silver': ('Commodity', 'http://stocks.investfunds.ru/indicators/view/225/'),
            'aluminium': ('Commodity', 'http://stocks.investfunds.ru/indicators/view/1565/'),
            # валютные пары
            'usd_rub': ('Currency', 'http://stocks.investfunds.ru/indicators/view/39/'),
            'eur_rub': ('Currency', 'http://stocks.investfunds.ru/indicators/view/132/'),
            'eur_usd': ('Currency', 'http://stocks.investfunds.ru/indicators/view/521/'),
            'gbp_usd': ('Currency', 'http://valuta.investfunds.ru/indicators/view/529/'),
            'eur_gbp': ('Currency', 'http://valuta.investfunds.ru/indicators/view/522/'),
            'eur_jpy': ('Currency', 'http://valuta.investfunds.ru/indicators/view/524/'),
            'usd_jpy': ('Currency', 'http://valuta.investfunds.ru/indicators/view/525/')
        }

        trials = 3
        for prop, (group, url) in props.iteritems():
            logging.info("Fetching %s data, url=%s" % (prop, url))
            trial = 0
            while True: # не больше 3 итераций
                trial += 1
                if trial > trials:
                    logging.error("Could not fetch the url %s (%s)" % (url, prop))
                    break

                try:
                    P = urlfetch.fetch(url, deadline=30)
                    break
                except DownloadError:
                    logging.warning("Trial #%d with url %s failed. Next trial" % (trial, url))
                    continue
                except DeadlineExceededError:
                    logging.error("DeadlineExceededError with %s" % url)
                    break
                else:
                    if P.status_code != 200:
                        logging.error("Status Code %d with url %s" % (P.status_code, url))

            root = lxhtml.fromstring(P.content)
            # Нужные ячейки (последние данные)
            tds = root.xpath('(//table[@class="table-data"])[3]/tr[2]/td')
            value = float(tds[1].text.replace(' ', ''))
            td0Text = tds[0].text_content().strip()
            if dateRE.match(td0Text):
                Date = datetime.strptime(td0Text, '%d.%m.%Y').date()
            elif timeRE.match(td0Text):
                Date = today
            else:
                logging.error("td0Text is not date nor time")
                continue

            model = groups[group]['model']
            entities = groups[group]['entities']

            if Date not in entities:
                entities[Date] = model.get_or_insert(key_name=Date.isoformat())
            setattr(entities[Date], prop, value)

        dates = set()
        for group in groups.itervalues():
            for entity in group['entities'].itervalues():
                entity.save()

        T1 = Time()

        self.response.write("It has been taken %.2f seconds<br>\n" % (T1-T0))



#class ErrorsReport(webapp2.RequestHandler) {{{1
class ErrorsReport(webapp2.RequestHandler):
    #def get(self) {{{2
    def get(self):
        """Раз в сутки просматриваются логи и, если в последние сутки были ошибки,
        то посылается сообщение на email администратора."""
        today = date.today()
        start_time = time.mktime((today-timedelta(days=1)).timetuple())
        logs = logservice.fetch(
            start_time = start_time,
            minimum_log_level = logservice.LOG_LEVEL_ERROR
        )
        # Чтобы узнать, были ли ошибки, нужно запросить первый элемент
        for log in logs:
            recipient = "wind29121982@gmail.com"
            sender = "Traceyourself-hrd tasks <wind29121982@gmail.com>"
            logs_page = "https://appengine.google.com/logs?&app_id=traceyourself-hrd&severity_level=3&severity_level_override=0&limit=10"
            subject = "Errors on traceyourself-hrd"
            body = """There were any errors on %s.\n\
            You may see them at %s""" % (today, logs_page)
            mail.send_mail(sender, recipient, subject, body)
            logging.info("Errors report has been sended")
            # после первого элемента завершаем цикл
            break


#app = webapp2.WSGIApplication(...) {{{1
app = webapp2.WSGIApplication([ #{{{1
                               ('/tasks/get_solar_data', GetSolarData),
                               ('/tasks/rp5', RP5),
                               ('/tasks/rp5_archive', RP5Archive),
                               ('/tasks/save_rp5_html', SaveRP5HTML),
                               ('/tasks/get_ec_data', GetEcData),
                               ('/tasks/errors_report', ErrorsReport),
                              ], debug=True)

