#coding: utf-8

"""
Принимает в качестве аргумента каталог страны и считает общее количество населённых пунктов
Количество населённых пунктов в регионе вытаскивает из названия файла
"""

###########
# Imports #
###########
import sys
import os
import re


##############
# Переменные #
##############
DIR = sys.argv[1]
count_rgx = re.compile(r'\((\d+)\)')


############
# Действие #
############
region_files = os.listdir(DIR)
total = 0
for filename in region_files:
    match = count_rgx.search(filename)
    if match is not None:
        count = int(match.group(1))
        total += count

print u"Общее количество населённых пунктов в каталоге %s = %d" % (DIR, total)
