#coding: utf-8
from time import time as T
import logging
import webapp2
from google.appengine.ext import db

from delete_data import DeleteModel, DeleteModelAttr, DeleteUser
from update_model import UpdateModel


class Test(webapp2.RequestHandler):
    def get(self):
        pass


class BuildAncestorPath(webapp2.RequestHandler):
    def get(self):
        """Преобразовать объекты моделей User, Prop и PropItem так,
        чтобы объекты Prop были детьми User, а объекты PropItem были детьми Prop.
        """
        T0 = Time()

        # from pprint import PrettyPrinter
        # class MyPrettyPrinter(PrettyPrinter):
            # def format(self, object, context, maxlevels, level):
                # if isinstance(object, unicode):
                    # return (object.encode('utf8'), True, False)
                # return PrettyPrinter.format(self, object, context, maxlevels, level)
        # pformat = MyPrettyPrinter(width=200).pformat
        #--------------------------------------------------------------------------------------
        U = User.all()
        data = {}
        for u in U:
            # self.response.write("<b>%s</b><br/>\n" % u.key().name())
            u_data = data[u.key().name()] = {}
            for prop in u.props:
                # self.response.write("%s (%s)<br/>\n" % (prop.prop_name, prop.prop_kind))
                u_data[prop.prop_name] = {
                    'kind': prop.prop_kind,
                    'comment': prop.prop_comment,
                    'items': {}
                }
                items = u_data[prop.prop_name]['items']
                for item in prop.propitems:
                    # self.response.write("&nbsp;&nbsp;&nbsp;&nbsp;%s {id:%d, type:%s, measure:%s, scale_attrs:%s}<br/>\n"
                        # % (item.item_name, item.key().id(), item.item_type, item.item_measure, item.scale_attrs))
                    items[item.item_name] = {
                        'id': item.key().id(),
                        'type':item.item_type,
                        'measure':item.item_measure,
                        'comment': item.item_comment,
                        'scale_attrs':item.scale_attrs
                    }
                    # Удаление элемента
                    item.delete()
                # Удаление свойства
                prop.delete()
            # self.response.write("<br/>\n")

        # self.response.write("<hr/>")
        
        # self.response.write("<pre>%s</pre>" % pformat(data))
        #--------------------------------------------------------------------------------------
        # Преобразование старых PropItem.id в новые
        id_map = {}
        # Создаём новые Prop и PropItem взамен старых
        for u, props in data.iteritems():
            u = User.get_by_key_name(u)
            for prop_name, prop_info in props.iteritems():
                # Создаём новый объект Prop
                p = Prop(parent=u, prop_kind=prop_info['kind'], prop_name=prop_name, prop_comment=prop_info['comment'], user=u)
                p.put()
                for item_name, item_info in prop_info['items'].iteritems():
                    # Создаём новый объект PropItem
                    pi = PropItem(parent=p, item_name=item_name, item_comment=item_info['comment'], user=u, prop=p)
                    pi.item_type = item_info['type']
                    if item_info['type'] in ('int', 'float') and item_info['measure']:
                        pi.item_measure = item_info['measure']
                    if item_info['type'] == 'scale':
                        if item_info['scale_attrs']:
                            pi.scale_attrs = item_info['scale_attrs']
                        else:
                            pi.scale_attrs = [0, 10, 1]
                    pi.put()
                    # Преобразование
                    id_map[item_info['id']] = pi.key().id()

        # self.response.write("<pre>%s</pre>" % pformat(id_map))
        #--------------------------------------------------------------------------------------
        # Изменение UserTrend согласно новым Prop и PropItem
        UTs = UserTrend.all()
        for UT in UTs:
            key_name = UT.key().name()
            date = UT.date
            u = UT.user
            id_values = []
            for prop in UT.dynamic_properties():
                value = getattr(UT, prop)
                id = int(prop[4:])
                if value is not None:
                    id_values.append( [id,value] )
            # Удаление записи в тренде
            UT.delete()
            # Создаём новую запись в тренде
            ut = UserTrend(parent=u, key_name=key_name, date=date, user=u)
            items_was = False
            for id_value in id_values:
                id = id_value[0]
                if id in id_map:
                    new_id = id_map[id]
                    prop = "item%d" % new_id
                    setattr(ut, prop, id_value[1])
                    items_was = True
            if items_was:
                ut.put()

        # self.response.write("<script>alert('DONE!')</script>")

        T1 = Time()
        self.response.write("It has been taken %.2f sec" % (T1-T0))


class CommonCityDataAncestorsAndUsers(webapp2.RequestHandler):
    """Задача: удалить все объекты CommonCityData, которые НЕ являются корневыми и заменить их
    корневыми аналогами.
    """
    def get(self):
        T0 = T()
        # импорты
        from datetime import date
        from google.appengine.runtime import apiproxy_errors
        from models import *

        # Эта дата определяется вручную (последняя дата, на которую свойство users пустое)
        last_date = date(2012, 6, 8)
        N = "All"
        CCDs = CommonCityData.gql("WHERE date <= :1 ORDER BY date DESC", last_date)
        if isinstance(N, int):
            CCDs = CCDs.fetch(N)

        try:
            for CCD in CCDs:
                if CCD.parent() is not None:
                    # собираем все свойства
                    kwargs = {
                        'key_name': CCD.key().name(),
                        # поля
                        'date': CCD.date,
                        'residence': CCD.residence,
                        #'users': ниже,
                        'from_archive': CCD.from_archive,
                        'temperature': CCD.temperature,
                        'cloud_cover': CCD.cloud_cover,
                        'precipitation': CCD.precipitation,
                        'pressure': CCD.pressure,
                        'humidity': CCD.humidity,
                        'wind_velocity': CCD.wind_velocity,
                        'wind_direction': CCD.wind_direction,
                        'sunrise': CCD.sunrise,
                        'sunset': CCD.sunset,
                        'day_duration': CCD.day_duration,
                        'moonrise': CCD.moonrise,
                        'moonset': CCD.moonset,
                        'moon_phase': CCD.moon_phase,
                        'moon_illuminated': CCD.moon_illuminated
                    }
                    # Последняя (не)обработанная дата
                    last_date = CCD.date
                    # logging.info("last date %s" % last_date.strftime('%d.%m.%Y'))
                    # Удаление объекта
                    CCD.delete()
                    # Восстановление объекта
                    e = CommonCityData(**kwargs)
                    e.put()
        except apiproxy_errors.OverQuotaError:
            self.response.write("Quota is over, last date %s<br>\n" % last_date.strftime('%d.%m.%Y'))
            T1 = T()
            self.response.write("Process has been taken %.2f sec.<br>\n" % (T1-T0))
        else:
            self.response.write("%s entities have been changed!<br>\n" % N)
            self.response.write("Last date %s<br>\n" % last_date.strftime('%d.%m.%Y'))
            T1 = T()
            self.response.write("Process has been taken %.2f sec.<br>\n" % (T1-T0))


app = webapp2.WSGIApplication([
    (r'/backends/test', Test),
    (r'/backends/build_ancestor_path', BuildAncestorPath),
    (r'/backends/commoncitydata_ancestors_and_users', CommonCityDataAncestorsAndUsers),
    # /delete_data/.*
    ('/delete_data/model', DeleteModel),
    ('/delete_data/model_attr', DeleteModelAttr),
    ('/delete_data/user', DeleteUser),
    # /update_model
    ('/update_model', UpdateModel),
], debug=True)


