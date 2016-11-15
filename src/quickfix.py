#coding: utf-8
# В backends.py находится другой класс Fix для особо долгоиграющих задач
# Imports {{{1
import webapp2
from time import time as Time
import logging

#}}}
#class ClearCommonProps(webapp2.RequestHandler) {{{1
class ClearCommonProps(webapp2.RequestHandler):
    def get(self):
        # U = User.all()
        # for u in U:
            # u.common_props = []
            # u.put()
        # self.response.write("SUCCESS")
        pass


#class RenameProperty(webapp2.RequestHandler) {{{1
class RenameProperty(webapp2.RequestHandler):
    """Переименовать свойство в какой-нибудь модели. Нужная вещь. Информация подчерпнута здесь:
    http://stackoverflow.com/questions/2906746/updating-model-schema-in-google-app-engine"""

    def get(self):
        T1 = Time()
        U = User.get_by_key_name('VPKulesh@gmail.com')
        UTs = UserTrend.all().ancestor(U)

        for UT in UTs:
            props = UT.dynamic_properties()
            for prop in props:
                if prop.startswith('item'):
                    value = getattr(UT, prop)
                    newProp = 'prop%s' % prop[4:]
                    setattr(UT, newProp, value)
                    delattr(UT, prop)
                    logging.warning("%s=%s ==> %s=%s" % (prop, value, newProp, value))
            UT.put()

        T2 = Time()
        self.response.write("It has been taken %.2f sec." % (T2-T1))


class FixSunAndMoonData(webapp2.RequestHandler): #{{{1
    """Начиная с 23.10.2014 данные по фазе и освещённости Луны собирались неправильно.
    Берём данные из resources/sun_and_moon_data.yaml, который генерируется скриптом
    download_sun_and_moon_data.py
    """
    def get(self): #{{{2
        import yaml
        from datetime import date, time
        from models import CommonCityData
        
        T1 = Time()

        with open('resources/sun_and_moon_data.yaml') as F:
            DATA = yaml.load(F)
        # Ключи первого уровня в DATA могут соответствовать нескольких объектам Residence
        Rmap = {
            'bangkok': ({'R_keyname':'id_170509', 'dateFrom':date(2014,10,28), 'dateTo':date.today()},),
            'nashville': ({'R_keyname':'id_257387', 'dateFrom':date(2014,10,28), 'dateTo':date.today()},),
            'saint-petersburg': (
                {'R_keyname':'id_7285', 'dateFrom':date(2014,8,12), 'dateTo':date.today()},
                {'R_keyname':'id_1536', 'dateFrom':date(2014,8,12), 'dateTo':date.today()},
                {'R_keyname':'id_3328', 'dateFrom':date(2014,8,12), 'dateTo':date.today()})
        }

        for city, dates in DATA.iteritems():
            if city in Rmap:
                for Rdata in Rmap[city]:
                    R_keyname, dateFrom, dateTo = Rdata['R_keyname'], Rdata['dateFrom'], Rdata['dateTo']
                    for Date, values in dates.iteritems():
                        if dateFrom <= Date <= dateTo:
                            CCD_keyname = '%s-%s' % (R_keyname, Date.strftime('%Y%m%d'))
                            CCD = CommonCityData.get_by_key_name(CCD_keyname)
                            CCD.sunrise = values['sunrise']
                            CCD.sunset = values['sunset']
                            # округление day_duration до минут
                            day_duration = values['day_duration']
                            h, m, s = day_duration.hour, day_duration.minute, day_duration.second
                            if s > 30 or (s==30 and m%2==1):
                                m += 1
                            if m == 60:
                                h += 1
                                m = 0
                            CCD.day_duration = time(h, m)
                            CCD.moonrise = values['moonrise']
                            CCD.moonset = values['moonset']
                            CCD.moon_phase = values['moon_phase']
                            CCD.moon_illuminated = int(round(values['moon_illuminated']))
                            CCD.save()

        T2 = Time()
        self.response.write("It has taken %.2f sec.<br>\n" % (T2-T1))
        #}}}
    #}}}
#class Kulesh(webapp2.RequestHandler) {{{1
class Kulesh(webapp2.RequestHandler):
    def get(self):
        """Создать пользователя для Кулеша В.П. Создать тестовые параметры и заполнить данными с
        различными распределениями.
        """
        T0 = Time()
        
        from google.appengine.api import users
        user = users.User("VPKulesh@gmail.com", "gmail.com")
        # Добавление статичных данных пользователя (prof.Profile.post.submit_static)
        city_id = "7285" # Санкт-Петербург
        keyname = "id_" + city_id
        R = Residence.get_by_key_name(keyname)
        # такое место жительства уже есть
        U = User(
            key_name = user.email(),
            user_obj = user,
            nickname = user.nickname(),
            residence = R,
            name = u'Валерий',
            surname = u'Кулеш',
            patronymic = u'Петрович',
            gender = 'M'
        )
        # Отмечаем общие параметры
        U.common_props = [u"solar_radio_flux", u"mean_planetary_A_index", u"mean_planetary_Kp_index", u"temperature", u"cloud_cover", u"precipitation", u"pressure", u"humidity", u"wind_velocity", u"wind_direction", u"day_duration", u"moon_phase", u"moon_illuminated"]
        U.put()
        # Добавляем параметры
        # 4 простых шкальных параметра. Потом будут добавляться id
        props = [
            {"name": u"Равномерное распределение"},
            {"name": u"Нормальное распределение μ=5 σ=1.5"},
            {"name": u"Бета распределение α=0.5 β=0.5"},
            {"name": u"Показательное распределение λ=1"}
        ]
        for prop_dict in props:
            prop = Prop(
                user = U,
                prop_name = prop_dict['name'],
                prop_kind = 'simple'
            )
            prop.put()
            propitem = PropItem(
                user = U,
                prop = prop,
                item_name = prop_dict['name'],
                item_type = 'scale',
                scale_attrs = [0, 10, 1]
            )
            propitem.put()
            # добавляем к словарю id. Нужно на фазе заполнения данными
            prop_dict['id'] = propitem.key().id()
        # 1 сложный параметр с 4 элементами. Потом будут добавляться id
        prop = Prop(
            user = U,
            prop_name = u"Реальные данные",
            prop_kind = "complex"
        )
        prop.put()
        propitems = [
            {"name":u"Средняя температура в Торонто", "type":"float", "measure":u"°C"},
            {"name":u"Курс евро к рублю", "type":"float", "measure":u"руб."},
            {"name":u"Количество активных доменов в зоне UZ", "type":"int", "measure":u"шт."},
            {"name":u"Цена на золото", "type":"float", "measure":u"руб./грамм"}
        ]
        for propitem_dict in propitems:
            propitem = PropItem(
                user = U,
                prop = prop,
                item_name = propitem_dict['name'],
                item_type = propitem_dict['type'],
                item_measure = propitem_dict['measure']
            )
            propitem.put()
            # добавляем к словарю id. Нужно на фазе заполнения данными
            propitem_dict['id'] = propitem.key().id()

        ################################
        # Заполнение тестовыми данными #
        ################################
        import random
        import csv
        # даты и данные по реальным данным хранятся во внешнем файле
        F = open('resources/real_test_data.csv')
        data = {}
        first_row_passed = False
        for row in csv.reader(F, delimiter=','):
            # первую строку пропускаем (заголовки)
            if not first_row_passed:
                first_row_passed = True
                continue
            Date = datetime.strptime(row[0], "%d.%m.%Y")
            chunk = []
            # равномерное распределение
            chunk.append(random.randint(0,10))
            # нормальное распределение
            x = random.normalvariate(mu=5, sigma=1.5)
            x = int(round(x))
            if x < 0: x = 0   # P(x<) = scipy.stats.norm.cdf(-0.5, 5, 1.5) = 1.23e-4
            if x > 10: x = 10 # P(x>10) = 1-scipy.stats.norm.cdf(10.5, 5, 1.5) = 1.23e-4
            chunk.append(x)
            # бета распределение
            x = random.betavariate(alpha=0.5, beta=0.5) * 10
            x = int(round(x))
            chunk.append(x)
            # показательное распределение
            x = random.expovariate(lambd=1)
            x = int(round(x))
            if x > 10: x = 10 # P(x>10) = 1-scipy.stats.expon.cdf(10.5, 1) = 7.5e-5
            chunk.append(x)
            # температура в Торонто
            x = float(row[1])
            chunk.append(x)
            # курс евро к рублю
            if row[2] != '':
                x = float(row[2])
            else:
                x = None
            chunk.append(x)
            # количество доменов
            x = int(row[3])
            chunk.append(x)
            # цена на золото
            if row[4] != '':
                x = float(row[4])
            else:
                x = None
            chunk.append(x)
            # присваиваем кусок данных дате
            data[Date] = chunk
        F.close()
        
        # Заносим данные из data в хранилище
        for Date, chunk in data.iteritems():
            keyname = U.nickname+"_"+Date.strftime("%Y%m%d")
            UT = UserTrend(key_name=keyname, date=Date.date(), user=U)
            # элементы простых параметров
            for i,prop_dict in enumerate(props):
                item_id_name = "item%d" % prop_dict['id']
                setattr(UT, item_id_name, chunk[i])
            # элементы сложных параметров
            for i,propitem_dict in enumerate(propitems):
                item_id_name = "item%d" % propitem_dict['id']
                if chunk[4+i] is not None:
                    setattr(UT, item_id_name, chunk[4+i])
            # сохранение
            UT.put()
            
        T1 = Time()
        self.response.write("It has taken %.2f sec.<br>\n" % (T1-T0))


#class AddTestData(webapp2.RequestHandler) {{{1
class AddTestData(webapp2.RequestHandler):
    def get(self):
        """Добавить тестовые данные. 
        * Данные добавляются пользователю TestData. Если его нет, то он создаётся.
        * Если у пользователя TestData есть параметры и тренд, затираем.
        * Город для пользователя выбирается из тех, за которые есть данные на заполняемые даты.
        * Тестовые данные должны содержать значения всех типов, а также пропуски (в тестовых целях).
        """
        from google.appengine.api import users
        import random
        
        T0 = Time()
        # создаём пользователя, если нет
        U = User.get_by_key_name('TestData@gmail.com')
        if U is None:
            U = User(
                key_name = "TestData@gmail.com",
                user_obj = users.User("TestData@gmail.com"),
                nickname = "TestData",
                residence = Residence.get_by_key_name('id_7285'), # Санкт-Петербург
                common_props = ['solar_radio_flux','mean_planetary_A_index','mean_planetary_Kp_index',
                    'temperature','cloud_cover','precipitation','pressure','humidity','wind_velocity',
                    'wind_direction','day_duration','moon_phase','moon_illuminated'] # все
            )
            U.put()
        
        # затираем данные пользователя
        db.delete(db.query_descendants(U))

        # создаём тестовые параметры всех типов
        @db.transactional
        def create_simple_prop(name, comment, type_, scale_attrs=[]):
            P = Prop(parent=U, prop_name=name, prop_kind='simple', prop_comment=comment)
            P.put()
            PI = PropItem(parent=U, prop=P, item_name=name, item_comment=comment, item_type=type_)
            PI.item_measure = ''
            if type_ == 'scale':
                PI.scale_attrs = scale_attrs
            PI.put()

        create_simple_prop('Scale', u'Шкаловые значения', 'scale', scale_attrs=[2,5,1])
        create_simple_prop('String', u'Строки', 'str')
        create_simple_prop('Integer', u'Целые числа', 'int')
        create_simple_prop('Float', u'Числа с плавающей точкой', 'float')
        create_simple_prop('Boolean', u'Булевы значения', 'bool')
        create_simple_prop('Time', u'Временные отметки', 'time')

        P = Prop(parent=U, prop_name='Complex', prop_kind='complex', prop_comment=u'Сложный параметр')
        P.put()

        @db.transactional
        def create_element(name, comment, type_, scale_attrs=[]):
            PI = PropItem(parent=U, prop=P, item_name=name, item_comment=comment, item_type=type_)
            PI.item_measure = ''
            if type_ == 'scale':
                PI.scale_attrs = scale_attrs
            PI.put()

        create_element('Scale', u'Шкаловые значения', 'scale', scale_attrs=[0,12,1])
        create_element('String', u'Строки', 'str')
        create_element('Integer', u'Целые числа', 'int')
        create_element('Float', u'Числа с плавающей точкой', 'float')
        create_element('Boolean', u'Булевы значения', 'bool')
        create_element('Time', u'Временные отметки', 'time')

        # заполнение тестовыми данными
        def get_random_value(type_, scale_attrs=[]):
            # 1/6, что значение будет None
            if random.randint(0,5) == 0:
                return None
            if type_ == 'scale':
                choices = range(scale_attrs[0], scale_attrs[1]+scale_attrs[2], scale_attrs[2])
                return random.choice(choices)
            elif type_ == 'str':
                chars = "abcdefghijklmnopqrstuvwxyz"
                string = ""
                for i in range(random.randint(3,6)):
                    string += random.choice(chars)
                return string
            elif type_ == 'int':
                return random.randint(0,100)
            elif type_ == 'float':
                return random.random() * 100
            elif type_ == 'bool':
                return random.choice((True, False))
            elif type_ == 'time':
                return datetime.strptime('%d:%d'%(random.randint(0,23), random.randint(0,59)), '%H:%M')


        Dates = (datetime.strptime('%d.2012'%day, '%j.%Y').date() for day in xrange(1,367)) # список дат
        PIs = PropItem.all().ancestor(U)
        for Date in Dates:
            keyname = "%s_%s" % (U.nickname, Date.strftime("%Y%m%d"))
            ccd_key = "%s-%s" % (U.residence.key().name(), Date.strftime("%Y%m%d"))
            UT = UserTrend(key_name=keyname, parent=U, date=Date, ccd_key=ccd_key)
            for PI in PIs:
                dyn_prop = 'item%d' % PI.key().id()
                value = get_random_value(PI.item_type, PI.scale_attrs)
                setattr(UT, dyn_prop, value)
            UT.put()

        T1 = Time()
        self.response.write("It has been taken %.2f sec<br>\n" % (T1-T0))


#class FixFalseFromArchive(webapp2.RequestHandler) {{{1
class FixFalseFromArchive(webapp2.RequestHandler):
    def get(self):
        """Скачать архив погоды во всем местам жительства за все даты, заканчивая вчерашней,
        если 'from_archive' == False.
        В данном случае для простоты мы скачиваем архив погоды для всех мест жительства
        с 23.05.2012 по вчерашнюю дату.
        """
        T0 = Time()
        from tasks import RP5Archive
        begin_date = date(2012, 5, 23)
        end_date = date.today() - timedelta(days=1)
        Date = begin_date
        while Date <= end_date:
            logging.warning("Processing date %s" % Date.strftime("%d.%m.%Y"))
            rp5_archive = RP5Archive()
            rp5_archive.get(day=Date)
            Date += timedelta(days=1)

        T1 = Time()
        self.response.write("It has taken %.2f sec." % (T1-T0))


#class MoveFalseToCCDM(webapp2.RequestHandler) {{{1
class MoveFalseToCCDM(webapp2.RequestHandler):
    def get(self):
        """Заполнить модель CommonCityDataMissed используя те объекты модели CommonCityData,
        у которых свойство from_archive==False и дата ранее сегодняшней."""
        today = date.today()
        CCDs = CommonCityData.all().filter('from_archive', False)
        for CCD in CCDs:
            if CCD.date < today:
                keyname = CCD.key().name()
                CCDM = CommonCityDataMissed(key_name=keyname, date=CCD.date, residence=CCD.residence)
                CCDM.put()

        self.response.write("DONE!<br>\n")


#class AddAstroData(webapp2.RequestHandler) {{{1
class AddAstroData(webapp2.RequestHandler):
    def get(self):
        import csv
        from datetime import datetime

        T0 = Time()
        F = open('resources/planets.csv')
        reader = csv.reader(F, delimiter=';')
        reader.next() # пропуск первой строки
        for row in reader:
            if row[0].startswith('2015'):
                Date = datetime.strptime(row[0], '%Y-%m-%d').date()
                sun_asc = float(row[1])
                sun_dec = float(row[2])
                sun_dis = float(row[3])
                moon_asc = float(row[4])
                moon_dec = float(row[5])
                moon_dis = float(row[6])
                mercury_asc = float(row[7])
                mercury_dec = float(row[8])
                mercury_dis = float(row[9])
                venus_asc = float(row[10])
                venus_dec = float(row[11])
                venus_dis = float(row[12])
                mars_asc = float(row[13])
                mars_dec = float(row[14])
                mars_dis = float(row[15])
                jupiter_asc = float(row[16])
                jupiter_dec = float(row[17])
                jupiter_dis = float(row[18])
                saturn_asc = float(row[19])
                saturn_dec = float(row[20])
                saturn_dis = float(row[21])
                uranus_asc = float(row[22])
                uranus_dec = float(row[23])
                uranus_dis = float(row[24])
                neptune_asc = float(row[25])
                neptune_dec = float(row[26])
                neptune_dis = float(row[27])
                pluto_asc = float(row[28])
                pluto_dec = float(row[29])
                pluto_dis = float(row[30])

                # Заносим в хранилище
                AD = AstroData(key_name=row[0], date=Date)
                AD.sun_asc = sun_asc
                AD.sun_dec = sun_dec
                AD.sun_dis = sun_dis
                AD.moon_asc = moon_asc
                AD.moon_dec = moon_dec
                AD.moon_dis = moon_dis
                AD.mercury_asc = mercury_asc
                AD.mercury_dec = mercury_dec
                AD.mercury_dis = mercury_dis
                AD.venus_asc = venus_asc
                AD.venus_dec = venus_dec
                AD.venus_dis = venus_dis
                AD.mars_asc = mars_asc
                AD.mars_dec = mars_dec
                AD.mars_dis = mars_dis
                AD.jupiter_asc = jupiter_asc
                AD.jupiter_dec = jupiter_dec
                AD.jupiter_dis = jupiter_dis
                AD.saturn_asc = saturn_asc
                AD.saturn_dec = saturn_dec
                AD.saturn_dis = saturn_dis
                AD.uranus_asc = uranus_asc
                AD.uranus_dec = uranus_dec
                AD.uranus_dis = uranus_dis
                AD.neptune_asc = neptune_asc
                AD.neptune_dec = neptune_dec
                AD.neptune_dis = neptune_dis
                AD.pluto_asc = pluto_asc
                AD.pluto_dec = pluto_dec
                AD.pluto_dis = pluto_dis
                AD.put()
        F.close()
        T1 = Time()
        self.response.write("It has been taken %.2f sec." % (T1-T0))


#class PropOrder(webapp2.RequestHandler) {{{1
class PropOrder(webapp2.RequestHandler):
    def get(self):
        """Присваиваем порядок пользовательским параметрам."""
        Us = User.all()
        for U in Us:
            Ps = Prop.all().ancestor(U).order('name')
            order = 1
            for P in Ps:
                P.order = order
                P.put()
                order += 1

        self.response.write("DONE")


#class AddEcData(webapp2.RequestHandler) {{{1
class AddEcData(webapp2.RequestHandler):
    #def get(self) {{{2
    def get(self):
        """Парсим сайт investfunds.ru и вытаскиваем данные с dateStart по dateEnd."""
        #def fetch(url) {{{3
        def fetch(url, **kwargs):
            trials = 3
            try:
                P = urlfetch.fetch(url, **kwargs)
            except DownloadError:
                logging.error("DownloadError with url %s" % url)
                raise
            except DeadlineExceededError:
                logging.error("DeadlineExceededError with url %s" % url)
                raise
            else:
                if P.status_code != 200:
                    logging.error("Status Code %d with url %s" % (P.status_code, url))
                    raise DownloadError
                else:
                    return P
        #}}}

        log = logging.info

        # Imports
        import re
        import lxml.html as lxhtml
        import urllib
        from google.appengine.api import urlfetch
        from google.appengine.api.urlfetch_errors import DownloadError, DeadlineExceededError

        # Переменные
        today = date.today()
        dateStart = date(2014, 9, 30)
        date0 = date(2012, 1, 1)
        dateEnd = today + timedelta(days=1)

        dateRE = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
        timeRE = re.compile(r'^\d{2}:\d{2}$')

        T0 = Time()

        props = {
            # индексы
            'micex': {'model':'Indice', 'url':'http://stocks.investfunds.ru/indicators/view/216/', 'dv':{}}, #dv=date->value
            'rts': {'model':'Indice', 'url':'http://stocks.investfunds.ru/indicators/view/218/', 'dv':{}},
            'dow': {'model':'Indice', 'url':'http://stocks.investfunds.ru/indicators/view/221/', 'dv':{}},
            'sap500': {'model':'Indice', 'url':'http://stocks.investfunds.ru/indicators/view/222/', 'dv':{}},
            'ftse100': {'model':'Indice', 'url':'http://stocks.investfunds.ru/indicators/view/223/', 'dv':{}},
            'sse': {'model':'Indice', 'url':'http://stocks.investfunds.ru/indicators/view/263/', 'dv':{}},
            # товары
            'oil': {'model':'Commodity', 'url':'http://stocks.investfunds.ru/indicators/view/624/', 'dv':{}},
            'gold': {'model':'Commodity', 'url':'http://stocks.investfunds.ru/indicators/view/224/', 'dv':{}},
            'silver': {'model':'Commodity', 'url':'http://stocks.investfunds.ru/indicators/view/225/', 'dv':{}},
            'aluminium': {'model':'Commodity', 'url':'http://stocks.investfunds.ru/indicators/view/1565/', 'dv':{}},
            # валютные пары
            'usd_rub': {'model':'Currency', 'url':'http://stocks.investfunds.ru/indicators/view/39/', 'dv':{}},
            'eur_rub': {'model':'Currency', 'url':'http://stocks.investfunds.ru/indicators/view/132/', 'dv':{}},
            'eur_usd': {'model':'Currency', 'url':'http://stocks.investfunds.ru/indicators/view/521/', 'dv':{}},
            'gbp_usd': {'model':'Currency', 'url':'http://valuta.investfunds.ru/indicators/view/529/', 'dv':{}},
            'eur_gbp': {'model':'Currency', 'url':'http://valuta.investfunds.ru/indicators/view/522/', 'dv':{}},
            'eur_jpy': {'model':'Currency', 'url':'http://valuta.investfunds.ru/indicators/view/524/', 'dv':{}},
            'usd_jpy': {'model':'Currency', 'url':'http://valuta.investfunds.ru/indicators/view/525/', 'dv':{}}
        }

        # Заполняем словари dv всеми датами, начиная с dateStart
        dates = []
        d = dateStart
        while d <= dateEnd:
            dates.append(d)
            d += timedelta(days=1)

        for prop in props.itervalues():
            for d in dates:
                prop['dv'][d] = None

        for propname, prop in props.iteritems():
            url = prop['url']
            log("Fetching %s data, url=%s" % (propname, url))
            baseUrl = url.split('.ru/')[0] + '.ru'

            # скачиваем базовую страницу индикатора
            P = fetch(url, deadline=30)
            root = lxhtml.fromstring(P.content)
            # Меняем дату "с"
            Ds = root.get_element_by_id('date_start')
            Ds.value = dateStart.strftime('%d.%m.%Y')
            F = root.xpath('//form[@name="sform"]')[0]

            # Отправка формы, перезагрузка страницы
            formValues = F.form_values()
            formData = urllib.urlencode(formValues)
            url = baseUrl + F.action
            P = fetch(url, payload=formData, method=urlfetch.POST, deadline=30,
                headers={'Content-Type':'application/x-www-form-urlencoded'})
            root = lxhtml.fromstring(P.content)

            try:
                pageCount = root.xpath('//select[@id="startlist"]/following-sibling::b')[0].text
            except IndexError: # когда одна страница, полей выбора страниц нет
                pageCount = 1

            # Переключаемся по страницам пока они не закончатся
            while True:
                if pageCount > 1:
                    pageSelected = root.xpath('//select[@id="startlist"]/option[@selected]')[0].text
                else:
                    pageSelected = 1
                log("Page %s of %s" % (pageSelected, pageCount))
                # Парсим таблицу с данными
                trs = root.xpath('(//table[@class="table-data"])[3]/tr')[1:]
                for tr in trs:
                    tds = tr.getchildren()
                    if len(tds) < 2:
                        log("len(tds) < 2")
                        continue
                    td0Text = tds[0].text_content().strip()

                    if dateRE.match(td0Text):
                        Date = datetime.strptime(td0Text, '%d.%m.%Y').date()
                    elif timeRE.match(td0Text):
                        Date = today
                    else:
                        logging.error("td0Text is not date nor time")
                        raise ValueError

                    value = float(tds[1].text.replace(' ', ''))

                    # Добавляем значение в словарь dv
                    prop['dv'][Date] = value

                # Переходим на следующую страницу, если она есть
                if pageCount > 1:
                    tdNext = root.xpath('//table[@summary="Pagination table"]//td[4]')[0]
                    a = tdNext.find('a')
                    if a is None: # страницы закончились
                        break

                    url = baseUrl + a.get('href')
                    P = fetch(url, deadline=30)
                    root = lxhtml.fromstring(P.content)
                    continue
                else:
                    break

        # Заполняем пустые значения в словарях dv
        log("Filling empty values")
        for prop in props.itervalues():
            dv = prop['dv']
            lastValue = None
            for d in dates:
                if dv[d] is None:
                    dv[d] = lastValue
                else:
                    lastValue = dv[d]

        # Заносим данные в хранилище
        log("Saving data into the datastore")
        for d in dates:
            # Данные раньше date0 не заносим
            if d < date0:
                continue
            if d.day == 1:
                log("Saving date %s" % d.isoformat())

            I = Indice.get_or_insert(key_name=d.isoformat(), date=d)
            Com = Commodity.get_or_insert(key_name=d.isoformat(), date=d)
            Cur = Currency.get_or_insert(key_name=d.isoformat(), date=d)

            for propname, prop in props.iteritems():
                value = prop['dv'][d]
                model = prop['model']
                if model == 'Indice':
                    setattr(I, propname, value)
                elif model == 'Commodity':
                    setattr(Com, propname, value)
                elif model == 'Currency':
                    setattr(Cur, propname, value)

            I.save()
            Com.save()
            Cur.save()

        T1 = Time()

        self.response.write("<br>It has been taken %.2f sec.<br>\n" % (T1-T0))
        log("AddEcData complete!")


#class AddEnResidencies(webapp2.RequestHandler) {{{1
class AddEnResidencies(webapp2.RequestHandler):
    #def get(self) {{{2
    def get(self):
        """Просто добавляем парочку населённых пунктов с url, ссылающимся на англискую версию.
        Нужны для контроля правильности парсинга погоды."""
        R = Residence(key_name='id_257387', id=257387, name='Nashville', url='http://rp5.ru/257387/en')
        R.put()
        R = Residence(key_name='id_170509', id=170509, name='Bangkok', url='http://rp5.ru/170509/en')
        R.put()
        self.response.write("Done!")


#class AddPropsLimit(webapp2.RequestHandler) {{{1
class AddPropsLimit(webapp2.RequestHandler):
    def get(self):
        Us = User.all()
        for U in Us:
            cPs = Prop.all().ancestor(U).count()
            if cPs > 6:
                propsLimit = cPs
            else:
                propsLimit = 6
            U.propsLimit = propsLimit
            U.put()

        self.response.write("Done!")


class FixMissedData(webapp2.RequestHandler): #{{{1
    def get(self): #{{{2
        import lxml.html as LH
        import re

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
        data = {}

        CCDPs = CommonCityDataPages.all()
        for CCDP in CCDPs:
            keyname = CCDP.key().name()
            id = keyname.split('_')[1].split('-')[0]
            if id not in data:
                data[id] = {}
            location = data[id]
            html = CCDP.html
            P = LH.fromstring(html)
            lang = P.get('lang')
            forecastTable = P.find('.//table[@id="forecastTable"]')
            trs = forecastTable.getchildren()
            Ds = []

            def td_groups(tr): #{{{3
                groups = []

                tds = tr.getchildren()[1:]
                col = 0
                for td in tds:
                    colspan = int(td.get('colspan', '1'))
                    if col == 0 or (col-firstColspan)%usualColspan == 0:
                        groups.append([])
                    groups[-1].append(td)
                    col += colspan

                return groups
            #}}}

            # Строка с датами
            tr = trs[0]
            tds = tr.getchildren()[1:]
            # для td_groups
            firstColspan = int(tds[0].get('colspan'))
            usualColspan = int(tds[1].get('colspan'))

            for td in tds:
                text = td.find('.//span[@class="monthDay"]').text
                if lang == 'ru':
                    day = int(text.split()[0]) # 28 октября
                elif lang == 'en':
                    day = int(text.split()[1].replace('.', '')) # October 28
                if day > 20:
                    month = 1
                else:
                    month = 2
                D = date(2015, month, day)
                if D not in location:
                    location[D] = {}
                Ds.append(D)

            # Строка с восходом и заходом Солнца
            tdGroups = td_groups(trs[10])
            for i,D in enumerate(Ds):
                sunrise = None
                sunset = None
                tdGroup = tdGroups[i]
                for td in tdGroup:
                    text = td.text
                    if not text or text.find(':') == -1: # время не указано
                        pass
                    else:
                        T = datetime.strptime(text, '%H:%M').time()
                        if 'litegrey' in td.get('class').split():   # заход
                            sunset = T
                        else:
                            sunrise = T
                if 'sunrise' not in location[D] or location[D]['sunrise'] is None:
                    location[D]['sunrise'] = sunrise
                if 'sunset' not in location[D] or location[D]['sunset'] is None:
                    location[D]['sunset'] = sunset

            # Строка с восходом и заходом Луны
            tdGroups = td_groups(trs[11])
            for i,D in enumerate(Ds):
                moonrise = None
                moonset = None
                tdGroup = tdGroups[i]
                for td in tdGroup:
                    text = td.text
                    if not text or text.find(':') == -1: # время не указано
                        pass
                    else:
                        T = datetime.strptime(text, '%H:%M').time()
                        if 'litegrey' in td.get('class').split():   # заход
                            moonset = T
                        else:
                            moonrise = T
                if 'moonrise' not in location[D] or location[D]['moonrise'] is None:
                    location[D]['moonrise'] = moonrise
                if 'moonset' not in location[D] or location[D]['moonset'] is None:
                    location[D]['moonset'] = moonset

            # Строка с фазой и освещённостью Луны
            tr = trs[12]
            tds = tr.getchildren()[1:] # количество ячеек равно таковому с датой
            for i in range(len(Ds)):
                td = tds[i]
                div = td.find('div')
                onmouseover = div.get('onmouseover')
                phrase = onmouseover.split("'")[1]
                moon_phase = phrase.split(',')[0]
                if lang == 'en':
                    moon_phase = phase_map[moon_phase]
                moon_illuminated = int(re.search(r'(\d+)%', phrase, re.U).group(1))
                D = Ds[i]
                location[D]['moon_phase'] = moon_phase
                location[D]['moon_illuminated'] = moon_illuminated

        self.response.write(data)

        # day_duration
        for id, location in data.iteritems():
            for D, dayData in location.iteritems():
                if dayData['sunrise'] and dayData['sunset']:
                    sunrise = datetime.strptime(dayData['sunrise'].isoformat(), "%H:%M:%S")
                    sunset = datetime.strptime(dayData['sunset'].isoformat(), "%H:%M:%S")
                    delta = sunset - sunrise
                    dayData['day_duration'] = datetime.strptime(str(delta), '%H:%M:%S').time()
                else:
                    dayData['day_duration'] = None
                keyname = "id_%s-%s" % (id, D.strftime('%Y%m%d'))
                CCD = CommonCityData.get_by_key_name(keyname)
                if CCD:
                    if CCD.sunrise is None and dayData['sunrise'] is not None:
                        CCD.sunrise = dayData['sunrise']
                    if CCD.sunset is None and dayData['sunset'] is not None:
                        CCD.sunset = dayData['sunset']
                    if CCD.moonrise is None and dayData['moonrise'] is not None:
                        CCD.moonrise = dayData['moonrise']
                    if CCD.moonset is None and dayData['moonset'] is not None:
                        CCD.moonset = dayData['moonset']
                    if CCD.day_duration is None and dayData['day_duration'] is not None:
                        CCD.day_duration = dayData['day_duration']
                    if CCD.moon_phase is None and dayData['moon_phase'] is not None:
                        CCD.moon_phase = dayData['moon_phase']
                    if CCD.moon_illuminated is None and dayData['moon_illuminated'] is not None:
                        CCD.moon_illuminated = dayData['moon_illuminated']

                    CCD.put()

        self.response.write(data)


# app = webapp2.WSGIApplication(...) {{{1
app = webapp2.WSGIApplication([
    (r'/quickfix/clear_common_props', ClearCommonProps),
    (r'/quickfix/rename_property', RenameProperty),
    (r'/quickfix/fix_sun_and_moon_data', FixSunAndMoonData),
    (r'/quickfix/kulesh', Kulesh),
    (r'/quickfix/add_test_data', AddTestData),
    (r'/quickfix/fix_false_from_archive', FixFalseFromArchive),
    (r'/quickfix/move_false_to_ccdm', MoveFalseToCCDM),
    (r'/quickfix/add_astro_data', AddAstroData),
    (r'/quickfix/prop_order', PropOrder),
    (r'/quickfix/add_ec_data', AddEcData),
    (r'/quickfix/add_en_residencies', AddEnResidencies),
    (r'/quickfix/add_props_limit', AddPropsLimit),
    (r'/quickfix/fix_missed_data', FixMissedData),
], debug=True)
