#coding: utf-8
#imports {{{1
import logging
from google.appengine.ext import db
from google.appengine.api import users
import datetime

# __all__ {{{1
__all__ = ['Residence', 'CommonData', 'AstroData', 'CommonCityData', 'CommonCityDataMissed',
    'CommonCityDataPages', 'Indice', 'Commodity', 'Currency', 'User', 'Prop', 'UserTrend']

#class Residence(db.Model) {{{1
class Residence(db.Model):
    """Список мест жительства пользователей.
    key_name = 'id_%s' % id"""
    id = db.IntegerProperty(required=True) # id населённого пункта
    name = db.StringProperty(required=True) # название населённого пункта
    url = db.StringProperty(required=True) # адрес прогноза погоды
    archive_url = db.StringProperty() # адрес архива погоды (url)
    # users - пользователи с данным местом жительства
    # daily_data - ежедневные данные погоды


#class CommonData(db.Model) {{{1
class CommonData(db.Model):
    """Ежедневные данные о солнечной активности с сайта www.tesis.lebedev.ru.
    key_name = date"""
    date = db.DateProperty(auto_now_add=True)
    solar_radio_flux = db.IntegerProperty()
    mean_planetary_A_index = db.IntegerProperty()
    mean_planetary_Kp_index = db.IntegerProperty()


#class AstroData(db.Model) {{{1
class AstroData(db.Model):
    """Ежедневные данные планет: [прямое восхождение, склонение, расстояние]
    key_name = date"""
    date = db.DateProperty(auto_now_add=True)
    sun_asc = db.FloatProperty(indexed=False)
    sun_dec = db.FloatProperty(indexed=False)
    sun_dis = db.FloatProperty(indexed=False)
    moon_asc = db.FloatProperty(indexed=False)
    moon_dec = db.FloatProperty(indexed=False)
    moon_dis = db.FloatProperty(indexed=False)
    mercury_asc = db.FloatProperty(indexed=False)
    mercury_dec = db.FloatProperty(indexed=False)
    mercury_dis = db.FloatProperty(indexed=False)
    venus_asc = db.FloatProperty(indexed=False)
    venus_dec = db.FloatProperty(indexed=False)
    venus_dis = db.FloatProperty(indexed=False)
    mars_asc = db.FloatProperty(indexed=False)
    mars_dec = db.FloatProperty(indexed=False)
    mars_dis = db.FloatProperty(indexed=False)
    jupiter_asc = db.FloatProperty(indexed=False)
    jupiter_dec = db.FloatProperty(indexed=False)
    jupiter_dis = db.FloatProperty(indexed=False)
    saturn_asc = db.FloatProperty(indexed=False)
    saturn_dec = db.FloatProperty(indexed=False)
    saturn_dis = db.FloatProperty(indexed=False)
    uranus_asc = db.FloatProperty(indexed=False)
    uranus_dec = db.FloatProperty(indexed=False)
    uranus_dis = db.FloatProperty(indexed=False)
    neptune_asc = db.FloatProperty(indexed=False)
    neptune_dec = db.FloatProperty(indexed=False)
    neptune_dis = db.FloatProperty(indexed=False)
    pluto_asc = db.FloatProperty(indexed=False)
    pluto_dec = db.FloatProperty(indexed=False)
    pluto_dis = db.FloatProperty(indexed=False)


#class CommonCityData(db.Model) {{{1
class CommonCityData(db.Model):
    """Ежедневные данные по городам модели Residence с сайта rp5.
    key_name = '%s-%s' % (Residence.key_name, date|%Y%m%d)"""
    date = db.DateProperty(auto_now_add=True)
    residence = db.ReferenceProperty(Residence, collection_name='daily_data')
    from_archive = db.BooleanProperty() # архивные данные или прогноз
    temperature = db.IntegerProperty(indexed=False)  # градусы Цельсия
    cloud_cover = db.IntegerProperty(indexed=False)  # %
    precipitation = db.FloatProperty(indexed=False)  # мм / 6 часов
    pressure = db.IntegerProperty(indexed=False)     # мм.рт.ст.
    humidity = db.IntegerProperty(indexed=False)     # %
    wind_velocity = db.IntegerProperty(indexed=False)# м/с
    wind_direction = db.StringProperty(choices = set(['NNE','NE','ENE','E','ESE','SE','SSE','S',
        'SSW','SW','WSW','W','WNW','NW','NNW','N','C']), indexed=False)
    sunrise = db.TimeProperty(indexed=False)
    sunset = db.TimeProperty(indexed=False)
    # Продолжительность солнечного дня вычисляется как разница
    day_duration = db.TimeProperty(indexed=False)
    moonrise = db.TimeProperty(indexed=False)
    moonset = db.TimeProperty(indexed=False)
    moon_phase = db.StringProperty(indexed=False)    # фаза луны (русские слова)
    moon_illuminated = db.IntegerProperty(indexed=False) # % освещённости луны в полночь


#class CommonCityDataMissed(db.Model) {{{1
class CommonCityDataMissed(db.Model):
    """Данные по городам модели Residence, по которым есть нескачанные архивы.
    key_name = '%s-%s' % (Residence.key_name, date|%Y%m%d)"""
    date = db.DateProperty(auto_now_add=True)
    residence = db.ReferenceProperty(Residence, collection_name='daily_data_missed', indexed=False)


#class CommonCityDataPages(db.Model) {{{1
class CommonCityDataPages(db.Model):
    """Код страниц, разбор которых вызвал ошибку.
    key_name = '%s-%s' % (Residence.key_name, date|%Y%m%d%H)"""
    datetime = db.DateTimeProperty(auto_now_add=True)
    html = db.TextProperty(required=True)


#class Indice(db.Model) {{{1
class Indice(db.Model):
    """Значения российских и мировых индексов
    key_name = date.isoformat()"""
    date = db.DateProperty(auto_now_add=True)
    micex = db.FloatProperty(indexed=False) # ММВБ
    rts = db.FloatProperty(indexed=False) # РТС
    dow = db.FloatProperty(indexed=False) # Dow Jones
    sap500 = db.FloatProperty(indexed=False) # S&P 500
    ftse100 = db.FloatProperty(indexed=False) # FTSE 100
    sse = db.FloatProperty(indexed=False) # SSE Composite


#class Commodity(db.Model) {{{1
class Commodity(db.Model):
    """Цены на сырьё
    key_name = date.isoformat()"""
    date = db.DateProperty(auto_now_add=True)
    oil = db.FloatProperty(indexed=False) # Нефть Brent, $/барр
    gold = db.FloatProperty(indexed=False) # Золото, руб/гр
    silver = db.FloatProperty(indexed=False) # Серебро, руб/гр
    aluminium = db.FloatProperty(indexed=False) # Алюминий, $/т


#class Currency(db.Model) {{{1
class Currency(db.Model):
    """Валютные пары
    key_name = date.isoformat()"""
    date = db.DateProperty(auto_now_add=True)
    usd_rub = db.FloatProperty(indexed=False)
    eur_rub = db.FloatProperty(indexed=False)
    eur_usd = db.FloatProperty(indexed=False)
    gbp_usd = db.FloatProperty(indexed=False)
    eur_gbp = db.FloatProperty(indexed=False)
    eur_jpy = db.FloatProperty(indexed=False)
    usd_jpy = db.FloatProperty(indexed=False)


#class User(db.Model) {{{1
class User(db.Model):
    """Статичные данные пользователей. children: Prop, UserTrend.
    key_name = user_obj.email()"""
    user_obj = db.UserProperty(required=True)
    nickname = db.StringProperty(required=True)
    name = db.StringProperty()
    surname = db.StringProperty()
    patronymic = db.StringProperty()
    gender = db.StringProperty(choices=set(['M','F']))
    birthdate = db.DateProperty()
    residence = db.ReferenceProperty(Residence, collection_name='users', required=True)
    # Общие параметры, которые учитываются при анализе
    common_props = db.StringListProperty()
    propsLimit = db.IntegerProperty(default=6)

#class Prop(db.Model) {{{1
class Prop(db.Model):
    """Пользовательские свойства. parent: User. Вместо key_name используется id."""
    name = db.StringProperty(required=True)
    type = db.StringProperty(required=True)
    order = db.IntegerProperty(required=True)
    measure = db.StringProperty() # prof.types_with_measure
    comment = db.StringProperty(multiline=True)
    scale_attrs = db.ListProperty(int) # if type == 'scale'; = [X₀, Xn, ΔX]

    def get_value(self, Date=None):
        """Получает значение параметра за определённую дату, по-умолчанию за сегодня."""
        if Date == None:
            Date = datetime.date.today()
        U = self.parent()
        key_name = "%s_%s" % (U.nickname, Date.strftime("%Y%m%d"))
        UT = UserTrend.get_by_key_name(key_name, parent=U)
        try:
            propname = "prop"+str(self.key().id())
            value = getattr(UT, propname)
        # Либо нет параметра, либо нет тренда на данную дату
        except AttributeError:
            value = ''  # пустое значение

        return value


#class UserTrend(db.Expando) {{{1
class UserTrend(db.Expando):
    """Тренд пользователя: значения пользовательских свойств по датам. parent: User
    key_name = '%s_%s' % (User.nickname, date|%Y%m%d)"""
    date = db.DateProperty(auto_now_add=True, required=True)
    ccd_key = db.StringProperty(required=True) # CommonCityData.key_name
    # Остальные свойства динамические: "prop<prop_id>" = value
