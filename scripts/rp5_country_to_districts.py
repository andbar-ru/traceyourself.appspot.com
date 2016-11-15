#coding: utf-8

""" {{{1
Скрипт парсит все страницы с сайта rp5.ru, посвящённые какой-либо стране
и формирует xml-файлы с информацией по регионам.
Иерархия: страна -> регион -> район -> населённый пункт
Нас интересует следующая информация:
* С региона:
    - название
    - количество населённых пунктов
* С населённых пунктов:
    - название
    - id
    - район
"""

# Imports {{{1
import lxml.html as LH
from lxml import etree
import re
import logging
import sys
from os import path, mkdir, chdir
import urllib
from time import sleep

# Variables {{{1
COUNTRY_PAGE = u'http://rp5.ru/Погода_в_России'
DIR = '/home/wind/GAE/traceyourself-hrd/rp5/Russia'
COUNTRY = u'Россия'
if not path.isdir(DIR):
    mkdir(DIR)
chdir(DIR)

# Регулярные выражения
count_rgx = re.compile(r"\b[\d']+\b")
id_rgx = re.compile(r'id=(\d+)')

# Logging {{{1
info_logger = logging.getLogger('info')
info_logger.addHandler(logging.StreamHandler(sys.stdout))
info_logger.setLevel(logging.INFO)
error_logger = logging.getLogger('errors')
error_logger.addHandler(logging.FileHandler('./errors.log', mode='w'))
error_logger.setLevel(logging.ERROR)

# Exceptions {{{1
class URLTraversed(Exception):
    """Исключение означает, что проход по данному URL уже осуществлялся"""
    pass

class URLMismatch(Exception):
    """Исключение означает, что url, по которому происходил переход,
    не соответствует url конечной страницы."""
    pass


#def parse(url) {{{1
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


#def traverse_links(countryMap, country) {{{1
def traverse_links(countryMap, region):
    global count, region_name_defined, true_region_name
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
                if not region_name_defined:
                    true_region_name = region_name
                    region_name_defined = True
                try:
                    district_name = path_parts[3]
                except IndexError:
                    district_name = ""
                # Проверка страны (всегда д.б. COUNTRY)
                country_name = path_parts[1]
                if country_name != COUNTRY:
                    error_logger.error("Country mismatch: %s != %s, url=%s" % (country_name, COUNTRY, P.docinfo.URL))
                    count += 1
                    return
                # Проверка региона
                if region_name != true_region_name:
                    error_logger.error("Region mismatch: %s != %s, url=%s" % (region_name, true_region_name, P.docinfo.URL))
                    count += 1
                    return
                # выясняем id пункта
                appMenu = P.find('//div[@id="appMenu"]')
                onclick = appMenu.xpath('.//li[text()="XML"]')[0].get('onclick')
                id = id_rgx.search(onclick).group(1)

                point = etree.SubElement(region, "point")
                etree.SubElement(point, "name").text = el.text
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
                    traverse_links(countryMap, region)
    return region


# Processing {{{1
country_page = LH.parse(COUNTRY_PAGE)
countryMap = country_page.xpath('//table[@class="countryMap"]')[0]
countryMap.make_links_absolute()
region_links = countryMap.xpath('//a[text()="..."]')

# Информация о стране
title = country_page.xpath('//div[@id="content"]//h1')[0].text # Заголовок "Погода в Украине в 29'928 населённых пунктах"
n = int(count_rgx.findall(title)[-1].replace("'", ""))         # Количество населённых пунктов в стране (29928)

# Временная обрезка списка регионов (для опытов)
# region_links  = region_links[:1]

urls_traversed = set([COUNTRY_PAGE])

regions_processed = [u'Алтайский край', u'Амурская область', u'Архангельская область',
    u'Астраханская область', u'Белгородская область', u'Брянская область', u'Владимирская область',
    u'Волгоградская область', u'Вологодская область', u'Воронежская область', u'Еврейская АО',
    u'Забайкальский край', u'Ивановская область', u'Иркутская область',
    u'Кабардино-Балкарская Республика', u'Калининградская область', u'Калужская область',
    u'Камчатский край', u'Карачаево-Черкесская Республика', u'Республика Адыгея',
    u'Республика Башкортостан', u'Республика Бурятия', u'Республика Дагестан',
    u'Республика Ингушетия', u'Республика Калмыкия']

for link in region_links:
    region_name = link.get('title')
    if region_name not in regions_processed:
        info_logger.info("Processing %s" % region_name)
        url = link.get('href')
        region_page = parse(url)
        countryMap = region_page.xpath('//table[@class="countryMap"]')[0]
        countryMap.make_links_absolute()
        region = etree.Element("region", name=region_name)
        count = 0   # Счётчик пройденных населённых пунктов
        region_name_defined = False # определено ди название региона (для проверки названия региона)
        true_region_name = ""       # название региона для сверки (определяется в traverse_links())
        traverse_links(countryMap, region)
        region.attrib['count'] = str(count)
        F = open("%s (%d).xml" % (region_name, count), "w")
        doc = etree.ElementTree(region)
        doc.write(F, encoding="utf-8", pretty_print=True)
        F.close()



