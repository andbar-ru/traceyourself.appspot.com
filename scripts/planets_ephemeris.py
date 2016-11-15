#coding: utf-8

"""
Скрипт вычисляет основные астрологические параметры планет:
- прямое восхождение (экваториальная долгота), градусы;
- склонение (экваториальная широта), градусы;
- расстояние, а.е.
с 01.01.2012 по 31.12.2015
и формирует csv-файл с полями (всего 31 поле):
дата
прямое восхождение \
склонение           > для каждой планеты
расстояние         /
Порядок планет: Солнце, Луна, Меркурий, Венера, Марс, Юпитер, Сатурн, Уран, Нептун, Плутон
"""
# Импорты
from os import path
import swisseph as swe
swe.set_ephe_path(path.expanduser('~/Programs/ephe/'))
from datetime import date, timedelta
import csv


# Переменные
CSV_FILE = '../data/planets.csv'
DATE_BEGIN = date(2012, 1, 1)
DATE_END = date(2015, 12, 31)
DATE_INC = timedelta(days=1)
PLANETS = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN,
    swe.URANUS, swe.NEPTUNE, swe.PLUTO]
FIELDS = ['date',
    'sun_asc', 'sun_dec', 'sun_dis',
    'moon_asc', 'moon_dec', 'moon_dis',
    'mercury_asc', 'mercury_dec', 'mercury_dis',
    'venus_asc', 'venus_dec', 'venus_dis',
    'mars_asc', 'mars_dec', 'mars_dis',
    'jupiter_asc', 'jupiter_dec', 'jupiter_dis',
    'saturn_asc', 'saturn_dec', 'saturn_dis',
    'uranus_asc', 'uranus_dec', 'uranus_dis',
    'neptune_asc', 'neptune_dec', 'neptune_dis',
    'pluto_asc', 'pluto_dec', 'pluto_dis']


# Действие
F = open(CSV_FILE, 'w')
writer = csv.writer(F, delimiter=';')
writer.writerow(FIELDS)

Date = DATE_BEGIN
while Date <= DATE_END:
    row = [Date.isoformat()]
    for planet in PLANETS:
        result = swe.calc_ut(swe.julday(Date.year, Date.month, Date.day), planet, swe.FLG_EQUATORIAL)
        row.extend(result[:3])
    writer.writerow(row)
    Date += DATE_INC

F.close()
