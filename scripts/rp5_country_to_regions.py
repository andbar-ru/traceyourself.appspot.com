#coding: utf-8

"""
Скрипт парсит все страницы с сайта rp5.ru, посвящённые какой-либо стране
и формирует _1_ xml-файл с информацией по стране.
Иерархия: страна -> регион -> населённый пункт
Нас интересует следующая информация:
* С населённых пунктов:
    - название
    - id
    - регион
"""

###########
# Imports #
###########
import lxml.html as LH
from lxml import etree
import re
import logging
import sys
from os import chdir
import urllib
from time import sleep

##############
# Переменные #
##############
COUNTRY_PAGE = u'http://rp5.ru/Погода_в_Эстонии'
DEST_DIR = '/home/wind/GAE/traceyourself-hrd/rp5/'
COUNTRY = u'Эстония'
chdir(DEST_DIR)

# Настройки журналирования
info_logger = logging.getLogger('info')
info_logger.addHandler(logging.StreamHandler(sys.stdout))
info_logger.setLevel(logging.INFO)
error_logger = logging.getLogger('errors')
error_logger.addHandler(logging.FileHandler('./errors.log', mode='w'))
error_logger.setLevel(logging.ERROR)

# Исключения
class URLTraversed(Exception):
    """Исключение означает, что проход по данному URL уже осуществлялся"""
    pass

class URLMismatch(Exception):
    """Исключение означает, что url, по которому происходил переход,
    не соответствует url конечной страницы."""
    pass

# Временная обрезка списка регионов (для опытов)
# all_links  = all_links[:1]

urls_traversed = set([COUNTRY_PAGE])

def parse(url):
    if url not in urls_traversed:
        try_count = 1   # номер попытки скачать страницу
        max_try_count = 5
        # Режим молотка
        while True:
            try:
                P = LH.parse(url)
                break
            except IOError: # Не получилось прочитать url
                if try_count == max_try_count:
                    raise
                sleep_seconds = try_count**2
                info_logger.warning("Couldn't read url %s. Try number %d. Sleeping %d sec" % (url, try_count, sleep_seconds))
                sleep(sleep_seconds)
                try_count += 1

        urls_traversed.add(url)
        if P.docinfo.URL != urllib.quote(url.encode('utf-8'), safe='/:()'):
            raise URLMismatch
        else:
            return LH.parse(url)
    else:
        raise URLTraversed


def traverse_links(countryMap, country):
    global count
    for link in countryMap.iterlinks():
        url = link[2]
        el = link[0]
        try:
            P = parse(url)
        except URLTraversed:
            pass
        except URLMismatch:
            count += 1
            error_logger.error("URLMismatch: %s, url=%s" % (el.text, url))
        else:
            forecast = P.xpath('//div[@id="content"]//table[@id="forecastTable"]')
            if forecast:    # лист (населённый пункт)
                # "Путь" к населённому пункту
                point_path = P.xpath('//div[@class="intoLeftNavi"]/span[@class="verticalBottom"]')[0]
                path_parts = [a.text_content() for a in point_path.iterchildren('a')]
                region_name = path_parts[2]
                try:
                    district_name = path_parts[3] # на случай повторов
                except IndexError:
                    district_name = ''
                # Проверка страны (всегда д.б. COUNTRY)
                country_name = path_parts[1]
                if country_name != COUNTRY:
                    error_logger.error("Country mismatch: %s != %s, url=%s" % (country_name, COUNTRY, P.docinfo.URL))
                    count += 1
                    return
                # выясняем id пункта
                appMenu = P.find('//div[@id="appMenu"]')
                onclick = appMenu.xpath('.//li[text()="XML"]')[0].get('onclick')
                id = id_rgx.search(onclick).group(1)

                point = etree.SubElement(country, "point")
                etree.SubElement(point, "name").text = el.text
                etree.SubElement(point, "region").text = region_name
                etree.SubElement(point, "district").text = district_name
                etree.SubElement(point, "id").text = id
                count += 1
                if count%10 == 0:
                    info_logger.info("%d. %s (%s) (id=%s)" % (count, el.text, region_name, id))
            else:           # ветка
                try:
                    countryMap = P.xpath('//table[@class="countryMap"]')[0]
                except IndexError:  # Нет списка городов и/или регионов -- пропускаем
                    continue
                else:
                    countryMap.make_links_absolute()
                    traverse_links(countryMap, country)
    return country


############
# Действие #
############
country_page = LH.parse(COUNTRY_PAGE)
countryMap = country_page.xpath('//table[@class="countryMap"]')[0]
countryMap.make_links_absolute()
all_links = countryMap.xpath('.//a')

# Регулярные выражения
count_rgx = re.compile(r"\b[\d']+\b")
id_rgx = re.compile(r'id=(\d+)')

# Информация о стране
title = country_page.xpath('//div[@id="content"]//h1')[0].text   # Заголовок "Погода в Эстонии в 64 населённых пунктах"
total_count = int(count_rgx.findall(title)[-1].replace("'", "")) # Количество населённых пунктов в стране (64)

count = 0   # Счётчик пройденных населённых пунктов
country = etree.Element("country", name=COUNTRY)

traverse_links(countryMap, country)

if count != total_count:
    info_logger.warning(u"ВНИМАНИЕ! Количество населённых пунктов в заголовке не совпадает с "
        u"количеством пройденных населённых пунктов: %d != %d" % (total_count, count))

country.attrib['count'] = str(count)
F = open("%s.xml" % COUNTRY, "w")
doc = etree.ElementTree(country)
doc.write(F, encoding="utf-8", pretty_print=True)
F.close()
