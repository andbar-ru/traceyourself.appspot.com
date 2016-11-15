#coding: utf-8
#Imports {{{1
import logging
import operator
from datetime import datetime, timedelta
import webapp2
from webapp2_extras.i18n import I18n, gettext
from babel.support import LazyProxy

#Global variables {{{1
AVAILABLE_LANGS = ['ru', 'en']
DEFAULT_LANG = 'en'


class MyLazyProxy(LazyProxy): #{{{1
    @property
    def value(self):
        """Кэширование не производится"""
        request = webapp2.get_request()
        i18n = get_i18n(request)
        func = i18n.gettext
        value = func(*self._args, **self._kwargs)
        return value

#def my_lazy_gettext(string, **variables) {{{1
def my_lazy_gettext(string, **variables):
    return MyLazyProxy(gettext, string, **variables)


def get_i18n(request): #{{{1
    """Возвращает существующий или новый объект webapp2_extras.i18n.I18n"""
    set_cookie = False
    # Во-первых, проверяем нажатие языковой кнопки
    lang = request.GET.get('lang', None)
    if lang is None:
        # Во-вторых, проверяем cookie
        # app.registry более не используем, так как одновременно задействовано >1 app.
        lang = request.cookies.get('lang', None)
        if lang is not None:
            if lang not in AVAILABLE_LANGS:
                lang = DEFAULT_LANG
                set_cookie = True
        else: # cookie не установлены
            # В-третьих, выбираем самый подходящий язык из заголовка 'Accept-Language'
            # ex: 'ru, en-US;q=0.8, en;q=0.6' 
            lang = request.accept_language.best_match(AVAILABLE_LANGS)
            if lang is None:
                lang = DEFAULT_LANG
            set_cookie = True
    else: # пользователь нажал языковую кнопку
        if lang not in AVAILABLE_LANGS:
            lang = DEFAULT_LANG
        set_cookie = True

    # Устанавливаем cookie, если требуется
    if set_cookie is True:
        expires = datetime.now() + timedelta(days=365)
        request.response.set_cookie('lang', lang, path='/', httponly=True, expires=expires)

    i18n = I18n(request)
    i18n.set_locale(lang)

    return i18n


#def most_common(L) {{{1
def most_common(L):
	"""Вспомогательная функция для функции summary_value.
	Возвращает наиболее частое значение в списке;
	а при равенстве частоты, то, у которого индекс больше."""
	# Создаём словарь с элементами value:[count, last_index]. Сортировка будет по значению
	D = {}
	for i,v in enumerate(L):
		try:
			count = D[v][0]
			D[v] = [count+1, i]	# счёт увеличивается, а индекс перезаписывается
		except KeyError:	# значение встречается впервые
			D[v] = [1, i]
	# И возвращаем его максимальный элемент
	return max(D.iteritems(), key=operator.itemgetter(1))[0]


#def summary_value(values, values_type, reverse=False) {{{1
def summary_value(values, values_type, reverse=False):
	"""Вычисляет сводное значение (чаще всего среднее) списка значений, основываясь на их типе.
	У всех значений тип д.б. одинаковый.
	values - итерируемый список значений;
	values_type - тип значений;
	reverse - инвертировать список (нужно, если тип = "str" и требуется,
	          чтобы приоритет был больше у первых значений)
	"""
	if values:	# список не пустой
		if values_type == 'int':	# обычное арифметическое среднее
			value = int(round(float(sum(values)) / len(values)))
		elif values_type == 'float_accumulative':	# на данный момент это только осадки, и мы считаем сумму
			value = sum(values)
		elif values_type == 'str':
			# в большинстве случаев все значения в списке будут одинаковыми
			if values.count(values[0]) == len(values):	# самый быстрый способ согласно http://stackoverflow.com/questions/38i44801/check-if-all-elements-in-a-list-are-identical
				value = values[0]
			else: # самое частое значение, либо, при равенстве, последнее/первое
				if reverse == True:
					values.reverse()
				value = most_common(values)
		else:
			raise ValueError
	else:
		return None
	# Всё в порядке, возвращаем сводное значение
	return value
