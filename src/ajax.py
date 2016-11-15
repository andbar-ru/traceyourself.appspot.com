#coding: utf-8
# Imports {{{1
from os import path
import logging
import json
from datetime import timedelta
# app engine
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import Key, GqlQuery
# проект
from models import *
import forms
from lib.functions import get_i18n

#Global variables {{{1
# для 'trend' и 'values', расчёты
def wind_direction_maps(_): #{{{2
    return {
        'value_angle': {
            'N':     0.0,
            'NNE':  22.5,
            'NE':   45.0,
            'ENE':  67.5,
            'E':    90.0,
            'ESE': 112.5,
            'SE':  135.0,
            'SSE': 157.5,
            'S':   180.0,
            'SSW': 202.5,
            'SW':  225.0,
            'WSW': 247.5,
            'W':   270.0,
            'WNW': 292.5,
            'NW':  315.0,
            'NNW': 337.5,
            'C':   ''
        },
        'angle_repr': { # json: представление в таблице
            0.0:   _(u'север'),
            22.5:  _(u'северо-северо-восток'),
            45.0:  _(u'северо-восток'),
            67.5:  _(u'востоко-северо-восток'),
            90.0:  _(u'восток'),
            112.5: _(u'востоко-юго-восток'),
            135.0: _(u'юго-восток'),
            157.5: _(u'юго-юго-восток'),
            180.0: _(u'юг'),
            202.5: _(u'юго-юго-запад'),
            225.0: _(u'юго-запад'),
            247.5: _(u'западо-юго-запад'),
            270.0: _(u'запад'),
            292.5: _(u'западо-северо-запад'),
            315.0: _(u'северо-запад'),
            337.5: _(u'северо-северо-запад'),
            '':    _(u'штиль')
        },
        # для графика распределения
        'categories': [_(u'С'),_(u'ССВ'),_(u'СВ'),_(u'ВСВ'),_(u'В'),_(u'ВЮВ'),
            _(u'ЮВ'),_(u'ЮЮВ'),_(u'Ю'),_(u'ЮЮЗ'),_(u'ЮЗ'),_(u'ЗЮЗ'),_(u'З'),
            _(u'ЗСЗ'),_(u'СЗ'),_(u'ССЗ')],
        'angle_cat': {
            0.0:   _(u'С'),
            22.5:  _(u'ССВ'),
            45.0:  _(u'СВ'),
            67.5:  _(u'ВСВ'),
            90.0:  _(u'В'),
            112.5: _(u'ВЮВ'),
            135.0: _(u'ЮВ'),
            157.5: _(u'ЮЮВ'),
            180.0: _(u'Ю'),
            202.5: _(u'ЮЮЗ'),
            225.0: _(u'ЮЗ'),
            247.5: _(u'ЗЮЗ'),
            270.0: _(u'З'),
            292.5: _(u'ЗСЗ'),
            315.0: _(u'СЗ'),
            337.5: _(u'ССЗ')
        },
        'cat_tooltip': {
            _(u'С'):   _(u'северный'),
            _(u'ССВ'): _(u'северо-северо-восточный'),
            _(u'СВ'):  _(u'северо-восточный'),
            _(u'ВСВ'): _(u'востоко-северо-восточный'),
            _(u'В'):   _(u'восточный'),
            _(u'ВЮВ'): _(u'востоко-юго-восточный'),
            _(u'ЮВ'):  _(u'юго-восточный'),
            _(u'ЮЮВ'): _(u'юго-юго-восточный'),
            _(u'Ю'):   _(u'южный'),
            _(u'ЮЮЗ'): _(u'юго-юго-западный'),
            _(u'ЮЗ'):  _(u'юго-западный'),
            _(u'ЗЮЗ'): _(u'западо-юго-западный'),
            _(u'З'):   _(u'западный'),
            _(u'ЗСЗ'): _(u'западо-северо-западный'),
            _(u'СЗ'):  _(u'северо-западный'),
            _(u'ССЗ'): _(u'северо-северо-западный'),
        },
        'angle_step': 22.5
    }
#}}}
def moon_phase_maps(_): #{{{2
    return {
        'value_angle': {
            # не переводим, т.к. в datastore хранятся русские названия
            u'Новолуние':            0.0,
            u'Растущий серп':       45.0,
            u'Первая четверть':     90.0,
            u'Растущая луна':      135.0,
            u'Полнолуние':         180.0,
            u'Убывающая луна':     225.0,
            u'Последняя четверть': 270.0,
            u'Убывающий серп':     315.0
        },
        'angle_repr': { # json: представление в таблице
            0.0:   _(u'новолуние'),
            45.0:  _(u'растущий серп'),
            90.0:  _(u'первая четверть'),
            135.0: _(u'растущая луна'),
            180.0: _(u'полнолуние'),
            225.0: _(u'убывающая луна'),
            270.0: _(u'последняя четверть'),
            315.0: _(u'убывающий серп')
        },
        # для графика распределения
        'categories': [_(u'Новолуние'),_(u'Растущий серп'),_(u'Первая четверть'),
            _(u'Растущая луна'),_(u'Полнолуние'),_(u'Убывающая луна'),
            _(u'Последняя четверть'),_(u'Убывающий серп')],
        'angle_cat': {
            0.0:   _(u'Новолуние'),
            45.0:  _(u'Растущий серп'),
            90.0:  _(u'Первая четверть'),
            135.0: _(u'Растущая луна'),
            180.0: _(u'Полнолуние'),
            225.0: _(u'Убывающая луна'),
            270.0: _(u'Последняя четверть'),
            315.0: _(u'Убывающий серп')
        },
        'cat_tooltip': {
            _(u'Новолуние'):          _(u'новолуние'),
            _(u'Растущий серп'):      _(u'растущий серп'),
            _(u'Первая четверть'):    _(u'первая четверть'),
            _(u'Растущая луна'):      _(u'растущая луна'),
            _(u'Полнолуние'):         _(u'полнолуние'),
            _(u'Убывающая луна'):     _(u'убывающая луна'),
            _(u'Последняя четверть'): _(u'последняя четверть'),
            _(u'Убывающий серп'):     _(u'убывающий серп')
        },
        'angle_step': 45.0
    }
#}}}
all_models = ( #{{{2
    'Indice',
    'Commodity',
    'Currency',
    'AstroData',
    'CommonData',
    'CommonCityData'
)
#}}}
def all_common_properties(_): #{{{2
    return {
        'Indice.micex': (_(u'ММВБ'), 'float', None),
        'Indice.rts': (_(u'РТС'), 'float', None),
        'Indice.dow': (_(u'Доу Джонс'), 'float', None),
        'Indice.sap500': (_(u'S&P 500'), 'float', None),
        'Indice.ftse100': (_(u'FTSE 100'), 'float', None),
        'Indice.sse': (_(u'SSE Composite'), 'float', None),
        'Commodity.oil': (_(u'Нефть Brent'), 'float', 'долл/барр'),
        'Commodity.gold': (_(u'Золото'), 'float', 'руб/гр'),
        'Commodity.silver': (_(u'Серебро'), 'float', 'руб/гр'),
        'Commodity.aluminium': (_(u'Алюминий'), 'float', 'долл/т'),
        'Currency.usd_rub': ('USD/RUB', 'float', None),
        'Currency.eur_rub': ('EUR/RUB', 'float', None),
        'Currency.eur_usd': ('EUR/USD', 'float', None),
        'Currency.gbp_usd': ('GBP/USD', 'float', None),
        'Currency.eur_gbp': ('EUR/GBP', 'float', None),
        'Currency.eur_jpy': ('EUR/JPY', 'float', None),
        'Currency.usd_jpy': ('USD/JPY', 'float', None),
        'AstroData.sun_asc': (_(u'Солнце, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.sun_dec': (_(u'Солнце, склонение'), 'float', u'\u00b0'),
        'AstroData.sun_dis': (_(u'Солнце, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.moon_asc': (_(u'Луна, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.moon_dec': (_(u'Луна, склонение'), 'float', u'\u00b0'),
        'AstroData.moon_dis': (_(u'Луна, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.mercury_asc': (_(u'Меркурий, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.mercury_dec': (_(u'Меркурий, склонение'), 'float', u'\u00b0'),
        'AstroData.mercury_dis': (_(u'Меркурий, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.venus_asc': (_(u'Венера, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.venus_dec': (_(u'Венера, склонение'), 'float', u'\u00b0'),
        'AstroData.venus_dis': (_(u'Венера, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.mars_asc': (_(u'Марс, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.mars_dec': (_(u'Марс, склонение'), 'float', u'\u00b0'),
        'AstroData.mars_dis': (_(u'Марс, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.jupiter_asc': (_(u'Юпитер, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.jupiter_dec': (_(u'Юпитер, склонение'), 'float', u'\u00b0'),
        'AstroData.jupiter_dis': (_(u'Юпитер, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.saturn_asc': (_(u'Сатурн, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.saturn_dec': (_(u'Сатурн, склонение'), 'float', u'\u00b0'),
        'AstroData.saturn_dis': (_(u'Сатурн, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.uranus_asc': (_(u'Уран, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.uranus_dec': (_(u'Уран, склонение'), 'float', u'\u00b0'),
        'AstroData.uranus_dis': (_(u'Уран, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.neptune_asc': (_(u'Нептун, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.neptune_dec': (_(u'Нептун, склонение'), 'float', u'\u00b0'),
        'AstroData.neptune_dis': (_(u'Нептун, расстояние от Земли'), 'float', _(u'а.е.')),
        'AstroData.pluto_asc': (_(u'Плутон, прямое восхождение'), 'circ', u'\u00b0'),
        'AstroData.pluto_dec': (_(u'Плутон, склонение'), 'float', u'\u00b0'),
        'AstroData.pluto_dis': (_(u'Плутон, расстояние от Земли'), 'float', _(u'а.е.')),
        'CommonData.solar_radio_flux': (_(u'Поток радиоизлучения (λ=10.7см)'), 'int', _(u'Ян')),
        'CommonData.mean_planetary_A_index': (_(u'Усреднённый планетарный A-индекс'), 'int', None),
        'CommonData.mean_planetary_Kp_index': (_(u'Усреднённый планетарный Kp-индекс'), 'scale', [0,9,1]),
        'CommonCityData.temperature': (_(u'Температура воздуха'), 'int', u'\u00b0C'),
        'CommonCityData.cloud_cover': (_(u'Облачность'), 'int', '%'),
        'CommonCityData.precipitation': (_(u'Осадки'), 'float', u'мм'),
        'CommonCityData.pressure': (_(u'Атмосферное давление'), 'int', _(u'мм\u00a0рт.ст.')),
        'CommonCityData.humidity': (_(u'Относительная влажность воздуха'), 'int', '%'),
        'CommonCityData.wind_velocity': (_(u'Скорость ветра'), 'int', _(u'м/с')),
        'CommonCityData.wind_direction': (_(u'Направление ветра'), 'circ_cat', wind_direction_maps(_)),
        'CommonCityData.sunrise': (_(u'Восход Солнца'), 'time', None),
        'CommonCityData.sunset': (_(u'Заход Солнца'), 'time', None),
        'CommonCityData.day_duration': (_(u'Продолжительность светового дня'), 'duration', None),
        'CommonCityData.moonrise': (_(u'Восход Луны'), 'time', None),
        'CommonCityData.moonset': (_(u'Заход Луны'), 'time', None),
        'CommonCityData.moon_phase': (_(u'Фаза Луны'), 'circ_cat', moon_phase_maps(_)),
        'CommonCityData.moon_illuminated': (_(u'Освещённость Луны'), 'int', '%')
    }
#}}}
#}}}
def format4json(value, data): #{{{1
    """Преобразует value в значение, используемое при расчётах. Помещается в trend и values"""
    if value is not None:
        type_ = data['type']
        if type_ == 'bool':
            return int(value)
        elif type_ == 'time': # в градусы
            return (value.hour*60 + value.minute)*0.25
        elif type_ == 'duration': # в часы
            return value.hour + value.minute/60.0
        elif type_ == 'circ_cat': # в градусы из словаря
            return data['maps']['value_angle'][value]
        elif type_ == 'float': # иначе будет 1.4000000000000001
            return round(value, 10)
        else: # scale, int, str, circ
            return value
    else:
        return None

#}}}
def check_json(JSON, U=None): #{{{1
    """Проверка JSON на правильность заполнения:
    Размеры списков 'trend' для каждого общего и пользовательского параметра и список 'dates' должны
    совпадать.
    Порядок дат (полагаемся на корректность функции build_json)
    Функция не влияет на работу скрипта, только заносит в журнал сообщения об ошибках.
    """
    nickname = U.nickname if U is not None else 'show_common_data'
    lens = set()
    if 'cProps' in JSON:
        for props in JSON['cProps'].itervalues():
            for prop in props['propsOrder']:
                lens.add(len(props[prop]['trend']))
    if 'uProps' in JSON:
        for prop_data in JSON['uProps'].itervalues():
            lens.add(len(prop_data['trend']))
    if len(lens) > 1:
        logging.error(json.dumps(JSON))
        logging.error("Sizes of 'trend' lists are not equal: lens: %s, user: %s" % (lens, nickname))
        return
    elif len(lens) == 0: # не было числовых параметров
        return

    # проверка того, что тренды включают все даты из UTs
    dates_size = len(JSON['dates'])
    trend_size = lens.pop()
    if trend_size != dates_size:
        logging.error(json.dumps(JSON))
        logging.error("JSON contains not all data of the trend: %d!=%d, user: %s" %
            (trend_size, dates_size, nickname))

#}}}
def build_json(UTs, U, _): #{{{1
    """Подготавливает все данные в формате JSON для передачи клиенту.
    Характеристики JSON:
    * В JSON включаются общие параметры, отмеченные пользователем и все пользовательские параметры.
    * Имена общих параметров имеют формат model.name. Это для упрощения обработки html и js.
    * Порядок важен для моделей и общих и пользовательских параметров, поэтому в дополнительных
      списках храним порядок.
    * В списках 'values' и 'trend' хранятся значения, приведённые к числовому виду.
    * Список 'values' содержит только непустые значения. Используется при расчёте статистических
      показателей и построении некоторых графиков.
    * Список 'trend' содержит значения за все даты тренда в таком же порядке, как и в списке 'dates'.
      Если значения за дату нет, то оно None. Используется при расчёте коэффициентов корреляции.
    * Даты переводятся в формат ISO.
    * Данные по всем параметрам и элементам должны быть за все даты, присутствующие в тренде.
      Если данных нет, то значение None.
    * Список 'dates' содержит все даты тренда.
    * Размеры списков 'trend' для каждого объекта, имеющего свойство 'trend', должны совпадать.
    * Всё остальное вычисляется и дополняется в JSON на стороне клиента.

    Схема JSON:
    {
      'dates': [все даты в UTs в формате ISO],
      'modelsOrder: [порядок моделей], # если отмечены какие-либо общие параметры
      'cProps': { # если отмечены какие-либо общие параметры
        model: { модели: 'AstroData', 'CommonData', 'CommonCityData'
          'propsOrder': [порядок общих параметров в данной модели]
          prop: { # для каждого параметра модели:
            'repr': представление в html,
            'type': тип значений,
            'measure': единицы измерения (если есть),
            'scaleAttrs': параметры шкалы (если type=='scale'),
            'maps': отображения (если type=='circ_cat'),
            'trend': [значения для всех дат в UTs],
            'values': [список непустых значений из 'trend'],
          },
          ...
        },
        ...
      },
      'uPropsOrder': [порядок пользовательских параметров],
      'uProps': {
        prop_id: { # для каждого пользовательского параметра:
          'repr': представление в html,
          'type': тип значений,
          'measure': единицы измерения (если есть),
          'scaleAttrs': параметры шкалы (если type=='scale'),
          'trend': [значения для всех дат в UTs],
          'values': [список непустых значений из 'trend'],
        },
        ...
      },
    }
    """
    empty_values = (None, '')
    allCommonProperties = all_common_properties(_)
    JSON = {
        'dates': [],
        #'modelsOrder': [],
        #'cProps': {},
        'uPropsOrder': [],
        'uProps': {}
    }

    # Собираем метаданные общих параметров, если отмечены
    if U.common_props:
        JSON['cProps'] = {}
        JSON['modelsOrder'] = []
        cProps = JSON['cProps']
        for prop in U.common_props:
            model = prop.split('.')[0]
            repr_, type_, smth = allCommonProperties[prop][0:3]
            prop_dict = {
                'repr': repr_,
                'type': type_,
                'trend': [],
                'values': []
            }
            if type_ in ('int', 'float', 'circ'):
                prop_dict['measure'] = smth
            elif type_ == 'scale':
                prop_dict['scaleAttrs'] = smth
            elif type_ == 'circ_cat':
                prop_dict['maps'] = smth

            if model not in cProps:
                JSON['modelsOrder'].append(model)
                cProps[model] = {}
                cProps[model]['propsOrder'] = []
            cProps[model][prop] = prop_dict
            cProps[model]['propsOrder'].append(prop)

    # Собираем метаданные пользовательских параметров
    Ps = Prop.all().ancestor(U).order('order')
    for P in Ps:
        id = P.key().id()
        prop = {
            'repr': P.name,
            'type': P.type,
            'trend': [],
            'values': [],
        }
        if P.type in ('int', 'float'):
            prop['measure'] = P.measure
        elif P.type == 'scale':
            prop['scaleAttrs'] = P.scale_attrs
        JSON['uProps'][id] = prop
        JSON['uPropsOrder'].append(id)

    # Собираем даты, тренд и ключи общих параметров
    Ks = {}
    for UT in UTs:
        Date = UT.date.isoformat()
        JSON['dates'].append(Date)
        # ключи общих параметров, если есть
        if 'cProps' in JSON:
            for model in all_models:
                if model in JSON['cProps']:
                    if model == 'CommonCityData':
                        K = Key.from_path(model, UT.ccd_key)
                    else:
                        K = Key.from_path(model, Date)
                    try:
                        Ks[model].append(K)
                    except KeyError:
                        Ks[model] = [K]
        # пользовательские параметры: prop\d+
        for prop_id, prop_data in JSON['uProps'].iteritems():
            dyn_prop = "prop%d" % prop_id
            value = getattr(UT, dyn_prop, None)
            value = format4json(value, prop_data)
            if value not in empty_values:
                prop_data['values'].append(value)
            prop_data['trend'].append(value) # в т.ч. None

    # Собираем значения общих параметров
    if 'cProps' in JSON:
        for model, props in JSON['cProps'].iteritems():
            objs = db.get(Ks[model])
            for obj in objs:
                for prop in props['propsOrder']:
                    propData = props[prop]
                    value = getattr(obj, prop.split('.')[1], None)
                    value = format4json(value, propData)
                    if value not in empty_values:
                        propData['values'].append(value)
                    propData['trend'].append(value) # в т.ч. None

    # Проверка трендов в JSON
    check_json(JSON, U)

    # Переводим в строковый вид
    JSON = json.dumps(JSON)

    return JSON

#}}}
def build_json_for_show_common_data(cProps, dateFrom, dateTo, residenceId, _): #{{{1
    """Подготавливает все данные в формате JSON для передачи клиенту.
    Характеристики JSON:
    * В JSON включаются только общие параметры, отмеченные пользователем в форме.
    * Имена общих параметров имеют формат model.name. Это для упрощения обработки html и js.
    * Порядок важен для моделей и параметров, поэтому в дополнительных списках храним порядок.
    * Погодные данные, если есть, загружаются для населённого пункта с id=residenceId.
    * В списках 'values' и 'trend' хранятся значения, приведённые к числовому виду.
    * Список 'values' содержит только непустые значения. Используется при расчёте статистических
      показателей и построении некоторых графиков.
    * Список 'trend' содержит значения за все даты тренда в таком же порядке, как и в списке 'dates'.
      Если значения за дату нет, то оно None. Используется при расчёте коэффициентов корреляции.
    * Даты переводятся в формат ISO.
    * Данные по всем параметрам должны быть за все даты с dateFrom по dateTo.
      Если данных нет, то значение None.
    * Список 'dates' содержит все даты с dateFrom по dateTo.
    * Размеры списков 'trend' для каждого объекта, имеющего свойство 'trend', должны совпадать.
    * Всё остальное вычисляется и дополняется в JSON на стороне клиента.

    Схема JSON:
    {
      'dates': [все даты с dateFrom по dateTo в формате ISO],
      'modelsOrder: [порядок моделей],
      'cProps': {
        model: { модели: 'CommonData','AstroData','CommonCityData','Indice','Commodity','Currency'
          'propsOrder': [порядок общих параметров в данной модели]
          prop: { # для каждого параметра модели:
            'repr': представление в html,
            'type': тип значений,
            'measure': единицы измерения (если есть),
            'scaleAttrs': параметры шкалы (если type=='scale'),
            'maps': отображения (если type=='circ_cat'),
            'trend': [значения для всех дат с dateFrom по dateTo],
            'values': [список непустых значений из 'trend'],
          },
          ...
        },
        ...
      }
    }
    """
    empty_values = (None, '')
    allCommonProperties = all_common_properties(_)
    JSON = {
        'dates': [],
        'modelsOrder': [],
        'cProps': {}
    }

    # Собираем метаданные общих параметров
    for prop in cProps:
        model = prop.split('.')[0]
        repr_, type_, smth = allCommonProperties[prop][0:3]
        propDict = {
            'repr': repr_,
            'type': type_,
            'trend': [],
            'values': []
        }
        if type_ in ('int', 'float', 'circ'):
            propDict['measure'] = smth
        elif type_ == 'scale':
            propDict['scaleAttrs'] = smth
        elif type_ == 'circ_cat':
            propDict['maps'] = smth

        if model not in JSON['cProps']:
            JSON['modelsOrder'].append(model)
            JSON['cProps'][model] = {}
            JSON['cProps'][model]['propsOrder'] = []
        JSON['cProps'][model][prop] = propDict
        JSON['cProps'][model]['propsOrder'].append(prop)

    # Собираем даты и ключи общих параметров
    Ks = {}
    curDate = dateTo # При обработке на клиенте необходима сортировка дат в обратном порядке
    while curDate >= dateFrom:
        Date = curDate.isoformat()
        JSON['dates'].append(Date)
        # ключи общих параметров
        for model in all_models:
            if model in JSON['cProps']:
                if model == 'CommonCityData':
                    K = Key.from_path(model, 'id_%s-%s' % (residenceId, Date.replace('-', '')))
                else:
                    K = Key.from_path(model, Date)
                try:
                    Ks[model].append(K)
                except KeyError:
                    Ks[model] = [K]
        curDate -= timedelta(days=1)
    # Собираем значения общих параметров
    for model, props in JSON['cProps'].iteritems():
        objs = db.get(Ks[model])
        for obj in objs:
            for prop in props['propsOrder']:
                propData = props[prop]
                value = getattr(obj, prop.split('.')[1], None)
                value = format4json(value, propData)
                if value not in empty_values:
                    propData['values'].append(value)
                propData['trend'].append(value) # в т.ч. None

    # Проверка трендов в JSON
    check_json(JSON)

    # Переводим в строковый вид
    JSON = json.dumps(JSON)

    return JSON

#}}}
class GetData(webapp2.RequestHandler): #{{{1
    """Получить все значения пользовательских и отмеченных общих параметров текущего пользователя."""
    def get(self): #{{{2
        # locale
        i18n = get_i18n(self.request)
        _ = i18n.gettext
        lang = i18n.locale

        user = users.get_current_user()

        if user is None: # такого быть не должно
            logging.error("user is None in GetData.get")
            raise ValueError

        U = User.get_by_key_name(user.email())

        if not U: # такого быть не должно
            logging.error("U is None in GetData.get")
            raise ValueError

        # Вытаскиваем ВЕСЬ тренд пользователя
        UTs = UserTrend.all().ancestor(U).order('-date')
        UTCount = UTs.count(limit=None)

        # Если тренда нет
        if UTCount == 0:
            warning = _(u'Тренда нет, заполнять его нужно <a href="/prof/fill_data">здесь</a>')
            JSON = json.dumps(warning)
            self.response.write(JSON)
            return

        UTs = UTs.run(limit=UTCount)
        JSON = build_json(UTs, U, _)
        self.response.write(JSON)
    #}}}
#}}}
class GetCommonData(webapp2.RequestHandler): #{{{1
    """Получить значения всех погодных показателей по заданному населённому пункту и диапазону дат.
    id населённого пункта и даты передаются в параметрах GET.
    """
    def get(self): #{{{2
        # locale
        i18n = get_i18n(self.request)
        _ = i18n.gettext
        lang = i18n.locale
        
        commonDataForm = forms.CommonDataForm(formdata=self.request.GET)

        if commonDataForm.validate():
            dateFrom = commonDataForm.dateFrom.data
            dateTo = commonDataForm.dateTo.data
            cProps = []
            for propGroup in ('indiceProps', 'commodityProps', 'currencyProps', 'geomagneticProps',
                              'weatherProps'):
                for prop in getattr(commonDataForm, propGroup).data:
                    cProps.append(prop)
            for prop in commonDataForm.astroProps.data:
                cProps.append(prop+'_asc')
                cProps.append(prop+'_dec')
                cProps.append(prop+'_dis')
            residenceId = commonDataForm.residence.data

            JSON = build_json_for_show_common_data(cProps, dateFrom, dateTo, residenceId, _)

            self.response.write(JSON)
        else:
            errors = []
            for fieldErrors in commonDataForm.errors.itervalues():
                for error in fieldErrors:
                    errors.append(unicode(error))
            self.response.write(json.dumps({'errors':errors}))
    #}}}
#}}}
app = webapp2.WSGIApplication([ #{{{1
    ('/get_data', GetData),
    ('/get_common_data', GetCommonData),
], debug=True)
