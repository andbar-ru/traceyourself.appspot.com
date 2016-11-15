# coding: utf-8
# Doc {{{1
"""
Скрипт производит следующие действия:
1. Очищает каталог DEST_DIR, в котором будет формироваться структура;
2. Анализирует структуру каталога SOURCE_DIR
3. В DEST_DIR создаётся каталог для каждого языка. Затем в каталоге каждого языка:
4. Создаётся файл countries с отображением страна:объект. Объект может быть:
    A. json-файлом, если страна в SOURCE_DIR представлена в виде xml-файла.
    B. Каталогом, если страна в SOURCE_DIR представлена в виде каталога. В каталоге:
        a. Создаётся файл regions с отображением регион:объект. Объект - json-файл.
5. Так как GAE позволяет в именах файлов использовать только ASCII-символы,
    то имена файлов -- это числа, а что означают числа, указано в файлах countries и regions.
"""

# Imports {{{1
from os import path, listdir, mkdir, chdir
from shutil import rmtree
from lxml import etree
import json
from time import time as T

# Variables {{{1
# Каталог, где находятся xml-файлы
SOURCE_DIR = path.expanduser(u'~/GAE/traceyourself-hrd/rp5/')
# Каталог, где создаётся структура
DEST_DIR = path.expanduser(u'~/GAE/traceyourself-hrd/src/rp5/')
# Парсер
parser = etree.XMLParser(encoding="utf-8")

# Processing {{{1
T0 = T()

# Очистка DEST_DIR
rmtree(DEST_DIR)
mkdir(DEST_DIR)

chdir(SOURCE_DIR)
for langDir in listdir('.'):
    sourceDir = path.join(SOURCE_DIR, langDir)
    destDir = path.join(DEST_DIR, langDir)
    if not path.isdir(destDir):
        mkdir(destDir)
    chdir(sourceDir)

    # Анализ каталога, создание словаря countries, файла countries.
    countries = {}
    n = 1
    for f in sorted(listdir('.')):
        if f.endswith('.xml') or path.isdir(f):
            if f.endswith('.xml'):
                f = f[:-4]
            countries[f.decode('utf-8')] = str(n)
            n += 1
    chdir(destDir)
    with open('countries', 'w') as F:
        # Не json.dump(countries, F), чтобы записать в файл русские буквы, а не \u041d...
        F.write((json.dumps(countries, ensure_ascii=False)).encode('utf-8'))

    # Анализ каждого элемента sourceDir
    for f in listdir(sourceDir):
        if f.endswith('.xml'): # f -- xml-файл
            print f
            P = etree.parse(path.join(sourceDir, f), parser)
            country = P.getroot()
            # формируем словарь с регионами {region: [(name, id, url, district),...]}
            regions = {}
            # формируем словарь со всеми пунктами {name: [(id, url, region, district),...]}
            allPoints = {}
            for point in country.iterchildren():
                region = point.find('region').text
                district = point.find('district').text
                name = point.find('name').text
                id = point.find('id').text
                url = "http://rp5.ru/%s/%s" % (id, langDir)
                # словарь с регионами
                if region not in regions:
                    regions[region] = [(name, id, url, district)]
                else:
                    regions[region].append( (name, id, url, district) )
                # словарь с населёнными пунктами
                if name not in allPoints:
                    allPoints[name] = [(id, url, region, district)]
                else:
                    allPoints[name].append( (id, url, region, district) )

            # allLocations в общем словаре нам нужен только в виде отсортированного списка списков
            allLocations = []
            for name in sorted(allPoints, key=lambda k: k.lower()):
                IURDs = allPoints[name] # id,url,region,district
                if len(IURDs) == 1:
                    id, url, region, district = IURDs[0]
                    allLocations.append( (name, id, url) )
                else:
                    # сначала составляем 2 списка для проверки дубликатов
                    NRs = [] # "name (region)"
                    IUDs = []
                    for id, url, region, district in IURDs:
                        NRs.append('%s (%s)' % (name, region))
                        IUDs.append( (id, url, district) )
                    # проверяем дубликаты
                    NR_indices = {}
                    for i,NR in enumerate(NRs):
                        if NR not in NR_indices:
                            NR_indices[NR] = [i]
                        else:
                            NR_indices[NR].append(i)
                    for NR, indices in NR_indices.iteritems():
                        if len(indices) > 1:
                            # прибавляем к имени ещё и район
                            for i in indices:
                                district = IUDs[i][2]
                                if district is not None:
                                    NRs[i] += ' (%s)' % district
                    # заносим в список
                    for i in xrange(len(NRs)):
                        allLocations.append( (NRs[i], IUDs[i][0], IUDs[i][1]) )

            # список allLocations включаем в словарь регионов
            regions['allLocations'] = allLocations
            # создаём json-файл
            filename = path.join(destDir, countries[f[:-4]])
            with open(filename, 'w') as F:
                F.write((json.dumps(regions, ensure_ascii=False)).encode('utf-8'))

        elif path.isdir(path.join(sourceDir, f)): # f -- каталог
            print f
            Dir = path.join(destDir, countries[f])
            mkdir(Dir)
            chdir(Dir)
            regions = {}
            n = 1
            for regionFile in sorted(listdir(path.join(sourceDir, f))):
                if regionFile.endswith('.xml'):
                    regions[regionFile[:-4]] = str(n)
                    n += 1
            with open('regions', 'w') as F:
                F.write((json.dumps(regions, ensure_ascii=False)).encode('utf-8'))

            # Анализ файлов регионов
            for regionFile in listdir(path.join(sourceDir, f)):
                if regionFile.endswith('.xml'):
                    regionName = regionFile[:-4]
                    # парсинг
                    P = etree.parse(path.join(sourceDir, f, regionFile), parser)
                    region = P.getroot()
                    # формируем словарь с районами {district: [(name, id, url),...]}
                    districts = {}
                    # формируем словарь с пунктами {name: [(id, url, district),...]}
                    allPoints = {}
                    for point in region.iterchildren():
                        district = point.find('district').text
                        if district is None:
                            district = regionName
                        name = point.find('name').text
                        id = point.find('id').text
                        url = "http://rp5.ru/%s/%s" % (id, langDir)
                        # словарь с районами
                        if district not in districts:
                            districts[district] = [(name, id, url)]
                        else:
                            districts[district].append( (name, id, url) )
                        # словарь с населёнными пунктами
                        if not name in allPoints:
                            allPoints[name] = [(id, url,district)]
                        else:
                            allPoints[name].append( (id, url,district) )

                    # allLocations в общем словаре нам нужен только в виде списка списков
                    allLocations = []
                    for name in sorted(allPoints, key=lambda k: k.lower()):
                        IUDs = allPoints[name]
                        if len(IUDs) == 1:
                            id, url, district = IUDs[0]
                            allLocations.append( (name, id, url) )
                        else:
                            for id, url, district in IUDs:
                                name1 = '%s (%s)' % (name, district)
                                allLocations.append( (name1, id, url) )
                    # список allLocations включаем в словарь районов
                    districts['allLocations'] = allLocations

                    # создаём json-файл
                    filename = path.join(Dir, regions[regionName])
                    with open(filename, 'w') as F:
                        F.write((json.dumps(districts, ensure_ascii=False)).encode('utf-8'))

        else:
            print u"Пропуск: %s" % f

T1 = T()
print u"Работа заняла %.2f сек." % (T1-T0)

# Проверка {{{1
# Проверка, что все страны есть, а также есть все регионы в больших странах.
# Проверка, что общее количество населённых пунктов в стране (регионе) равно сумме
#населённых пунктов по регионам (районам).
chdir(DEST_DIR)
for langDir in listdir('.'):
    chdir(langDir) # вход в каталог языка
    # проверяем, что все страны есть
    with open('countries') as F:
        countries = json.load(F)
    for c in countries.itervalues():
        assert path.exists(c)

    for node in countries.itervalues(): # проходим по странам
        if path.isdir(node): # большая страна
            chdir(node) # вход в каталог страны
            # проверяем, что все регионы есть
            with open('regions') as F:
                regions = json.load(F)
            for r in regions.itervalues():
                assert path.isfile(r)

            for regionFile in regions.itervalues():
                with open(regionFile) as F:
                    # проверяем, что общее количество н.п. в регионе == сумме н.п. по районам
                    region = json.load(F)
                    N = len(region['allLocations'])
                    nSum = 0
                    for district, locations in region.iteritems():
                        if district != 'allLocations':
                            nSum += len(locations)
                    try:
                        assert nSum == N
                    except AssertionError:
                        print("AssertionError: %d != %d (страна %s, регион %s)" %
                            (nSum, N, node, regionFile))
            chdir('..') # выход из каталога страны

        else:
            with open(node) as F:
                # проверяем, что общее количество н.п. в стране == сумме н.п. по регионам
                country = json.load(F)
                N = len(country['allLocations'])
                nSum = 0
                for region, locations in country.iteritems():
                    if region != 'allLocations':
                        nSum += len(locations)
                try:
                    assert nSum == N
                except AssertionError:
                    print "AssertionError: %d != %d (страна %s)" % (nSum, N, node)
    chdir('..') # выход из каталога языка

print u"Проверка пройдена успешно"


