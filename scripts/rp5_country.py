#coding: utf-8

# Doc {{{1
"""
Скрипт парсит все страницы с сайта rp5.ru, посвящённые какой-либо стране
и формирует xml-файлы с информацией по странам.
Иерархия: страна -> регион -> населённый пункт
Нас интересует следующая информация:
* С населённых пунктов:
    - название
    - id
    - регион
    - район (в случае наличия повторов)
"""

# Imports {{{1
import lxml.html as LH
from lxml import etree
import re
import logging
import sys
from os import path, chdir, mkdir, listdir
from shutil import rmtree
import urllib
from time import sleep

# Variables {{{1
# Определение языка
langs = ('ru', 'en')
try:
    LANG = sys.argv[1]
except IndexError:
    print u"Нужно указать язык."
    sys.exit(1)
if LANG not in langs:
    print u"Неправильный язык: %s" % LANG
    sys.exit(1)

if LANG == 'ru':
    WORLD_PAGE = u'http://rp5.ru/Погода_в_мире'
elif LANG == 'en':
    WORLD_PAGE = u'http://rp5.ru/Weather_in_the_world'

DIR = path.expanduser('~/GAE/traceyourself-hrd/rp5/%s' % LANG)
if not path.isdir(DIR):
    mkdir(DIR)
chdir(DIR)

# Регулярные выражения
count_rgx = re.compile(r"\b\d+\b")
id_rgx = re.compile(r'id=(\d+)')
# пройденные урлы (чтобы повторно не парсить)
urlsTraversed = set([WORLD_PAGE])

# Logging {{{1
info_logger = logging.getLogger('info')
info_logger.addHandler(logging.StreamHandler(sys.stdout))
info_logger.setLevel(logging.INFO)
error_logger = logging.getLogger('errors')
error_logger.addHandler(logging.FileHandler('./errors.log', mode='w+'))
error_logger.setLevel(logging.ERROR)

# Exceptions {{{1
class URLTraversed(Exception):
    """Исключение означает, что проход по данному URL уже осуществлялся"""
    pass

class URLMismatch(Exception):
    """Исключение означает, что url, по которому происходил переход,
    не соответствует url конечной страницы."""
    pass

class DownloadError(IOError):
    """Не удалось прочитать url."""
    pass

#def parse(url) {{{1
def parse(url):
    if url not in urlsTraversed:
        try_count = 1   # номер попытки скачать страницу
        max_try_count = 5
        # Режим молотка
        while True:
            try:
                P = LH.parse(url)
                break
            except IOError: # Не получилось прочитать url
                if try_count == max_try_count:
                    raise DownloadError
                sleep_seconds = try_count**2
                info_logger.warning("Couldn't read url %s. Try number %d. Sleeping %d sec" % (url, try_count, sleep_seconds))
                sleep(sleep_seconds)
                try_count += 1

        urlsTraversed.add(url)
        if P.docinfo.URL != urllib.quote(url.encode('utf-8'), safe="/:'(),"):
            raise URLMismatch
        else:
            return P
    else:
        raise URLTraversed


#def traverse_links(countryMap, E, elem='country') {{{1
def traverse_links(countryMap, E, elem='country'):
    global count, countryName, regionName
    for link in countryMap.iterlinks():
        url = link[2]
        el = link[0]
        try:
            P = parse(url)
        except URLTraversed:
            pass
        except URLMismatch:
            count += 1
            error_logger.error("URLMismatch: country=%s, url=%s" % (E.get('name'), url))
        except DownloadError:
            error_logger.error('ERROR: finally could not read url %s.' % url)
        else:
            forecast = P.xpath('//div[@id="content"]//table[@id="forecastTable"]')
            if forecast:    # лист (населённый пункт)
                # "Путь" к населённому пункту
                point_path = P.xpath('//div[@class="intoLeftNavi"]/span[@class="verticalBottom"]')[0]
                path_parts = [a.text_content() for a in point_path.iterchildren('a')]
                curRegionName = path_parts[2]
                try:
                    dictrictName = path_parts[3] # на случай повторов
                except IndexError:
                    dictrictName = ''
                # Проверка страны (всегда д.б. countryName)
                curCountryName = path_parts[1]
                if curCountryName != countryName:
                    error_logger.error("Country mismatch: %s != %s, url=%s" % (curCountryName, countryName, P.docinfo.URL))
                    count += 1
                    return
                # Проверка региона
                if elem == 'region' and curRegionName != regionName:
                    error_logger.error("Region mismatch: %s != %s, url=%s" % (curRegionName, regionName, P.docinfo.URL))
                # выясняем id пункта
                appMenu = P.find('//div[@id="appMenu"]')
                onclick = appMenu.xpath('.//li[text()="XML"]')[0].get('onclick')
                id = id_rgx.search(onclick).group(1)

                point = etree.SubElement(E, "point")
                etree.SubElement(point, "name").text = el.text
                if elem != 'region':
                    etree.SubElement(point, "region").text = curRegionName
                etree.SubElement(point, "district").text = dictrictName
                etree.SubElement(point, "id").text = id
                count += 1
                if count%10 == 0:
                    info_logger.info("%d. %s (%s) (id=%s)" % (count, el.text, curRegionName, id))
            else:           # ветка
                try:
                    countryMap = P.xpath('//table[@class="countryMap"]')[0]
                except IndexError:  # Нет списка городов и/или регионов -- пропускаем
                    continue
                else:
                    countryMap.make_links_absolute()
                    traverse_links(countryMap, E)
    return E


# Processing {{{1
# Какие страны не участвуют
countriesExclude = [file[:-4].decode('utf-8') for file in listdir('.') if file.endswith('.xml')] # файлы
countriesExclude.extend([node.decode('utf-8') for node in listdir('.') if path.isdir(node)]) # каталоги
# Какие страны участвуют
countriesInclude = []
# Какие регионы не участвуют
regionsExclude = []

Pworld = LH.parse(WORLD_PAGE)
countryMap = Pworld.find('.//table[@class="countryMap"]')
countryMap.make_links_absolute()
countryLinks = countryMap.xpath('.//b/a')

for link in countryLinks:
    countryName = link.text

    if countryName not in countriesExclude:
    # if countryName in countriesInclude:
        countryPage = LH.parse(link.get('href'))
        # Информация о стране
        # Заголовок "Погода в Эстонии в 64 населённых пунктах"
        title = countryPage.xpath('//div[@id="content"]//h1')[0].text.replace("'", "")
        # Количество населённых пунктов в стране (64)
        total_count = int(count_rgx.findall(title)[-1])
        info_logger.info('%s (%d)' % (countryName, total_count))
        countryMap = countryPage.find('.//table[@class="countryMap"]')
        countryMap.make_links_absolute()
        # Если населённых пунктов очень много, то скачиваем страну по регионам
        if total_count > 5000:
            # Создаём каталог и входим в него
            if not path.exists(countryName):
                mkdir(countryName)
            chdir(countryName)

            regionLinks = countryMap.xpath('//a[span[text()=">>>"]]')

            for link in regionLinks:
                regionName = link.get('title')
                if regionName not in regionsExclude:
                    info_logger.info("Processing %s" % regionName)
                    url = link.get('href')
                    regionPage = LH.parse(url)
                    regionMap = regionPage.xpath('//table[@class="countryMap"]')[0]
                    regionMap.make_links_absolute()
                    region = etree.Element("region", name=regionName)
                    count = 0
                    traverse_links(regionMap, region, elem='region')
                    region.attrib['count'] = str(count)
                    F = open("%s.xml" % regionName, 'w')
                    doc = etree.ElementTree(region)
                    doc.write(F, encoding="utf-8", pretty_print=True)
                    F.close()

            chdir('..')

        else: # total_count > 5000
            count = 0   # Счётчик пройденных населённых пунктов
            country = etree.Element("country", name=countryName)
            # Проход по всем ссылкам рекурсивно
            traverse_links(countryMap, country)

            if count != total_count:
                info_logger.warning(u"ВНИМАНИЕ! Количество населённых пунктов в заголовке не совпадает с "
                    u"количеством пройденных населённых пунктов: %d != %d" % (total_count, count))

            country.attrib['count'] = str(count)
            F = open("%s.xml" % countryName, "w")
            doc = etree.ElementTree(country)
            doc.write(F, encoding="utf-8", pretty_print=True)
            F.close()
