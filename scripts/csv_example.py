#coding: utf-8

"""
Скрипт создаёт csv-файл с данными, который служит в качестве примера на странице /prof/analysis_test
"""
# Импорты
from os import path
from datetime import date, timedelta
import random
import csv


# Переменные
CSV_FILE = '../src/doc/csv_example.csv'
DATE_BEGIN = date(2012, 1, 1)
DATE_END = date(2015, 12, 31)
DATE_INC = timedelta(days=1)
header = ['date', 'int_data, int', 'float_data, float', 'bool_data1, bool', 'bool_data2, bool',
          'scale_data, scale, [0,100,5]', 'time_data1, time', 'time_data2, time']
bool_values = ['true', 'false', '0', '1', '+', '-', 'да', 'нет']

# 'wrong_header', 'shuffle_dates', 'duplicate_dates', 'wrong_cols', 'change_symbols', 'wrong_dates'
ERROR = '';
if ERROR:
    CSV_FILE = '../src/doc/invalid_csv_example.csv'

# Действие
F = open(CSV_FILE, 'w')
writer = csv.writer(F, delimiter=';')

if ERROR == 'wrong_header': # корёжим заголовок
    symbols = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()_-+=[]{};:'"\\|/?,.<>'''
    header = list(';'.join(header))
    n = 3 # количество изменений
    for i in range(n):
        index = random.randint(0, len(header)-1)
        symbol = random.choice(symbols)
        header[index] = symbol
    header = ''.join(header).split(';')

writer.writerow(header)

# Собираем даты
dates = []
Date = DATE_BEGIN
while Date <= DATE_END:
    if ERROR == 'duplicate_dates' and random.random() < 0.01:
        d = random.choice(dates)
        dates.append(d)
    else:
        dates.append(Date)
    Date += DATE_INC

if ERROR == 'shuffle_dates': # тасуем даты
    random.shuffle(dates)

for Date in dates:
    row = []
    for field in header:
        r = random.random()

        if field == 'date':
            value = Date.strftime('%d.%m.%Y')
        elif field == 'int_data, int':
            if r > 0.1:
                value = random.randint(-50,50)
            else:
                value = '--'
        elif field == 'float_data, float':
            if r > 0.1:
                value = "%0.3f" % (random.random() * 100 - 50)
            else:
                value = ''
        elif field == 'bool_data1, bool' or field == 'bool_data2, bool':
            if r > 0.1:
                value = random.choice(bool_values)
            else:
                value = '--'
        elif field == 'scale_data, scale, [0,100,5]':
            if r > 0.1:
                value = random.choice(range(0,101,5))
            else:
                value = ''
        elif field == 'time_data1, time' or field == 'time_data2, time':
            if r > 0.1:
                HH = random.randint(0, 23)
                MM = random.randint(0, 59)
                value = "%02d:%02d" % (HH, MM)
            else:
                value = '--'

        row.append(value)

    # Введение ошибки
    if ERROR == 'wrong_cols': # делаем количество столбцов непостоянным
        r = random.random()
        if r < 0.1:
            d = random.randint(-3,3)
            if d < 0:
                d = -d
                for i in range(d):
                    row.pop()
            elif d > 0:
                for i in range(d):
                    row.append(random.randint(0, 10))
            else:
                pass

    elif ERROR == 'change_symbols': # меняем случайные символы в строке на случайные
        # symbols = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()_-+=[]{} :'"\\|/?,.<>'''
        symbols = '01234567890'
        r = random.random()
        if r < 0.3:
            row = list(';'.join(map(str, row))) # список символов
            n = random.randint(1,3) # Количество изменений
            for i in range(n):
                index = random.randint(0, len(row)-1)
                if row[index] != ';':
                    symbol = random.choice(symbols)
                    row[index] = symbol
            row = ''.join(row).split(';')

    elif ERROR == 'wrong_dates': # корёжим даты
        #symbols = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()_-+=[]{};:'"\\|/?,.<>'''
        symbols = '01234567890'
        r = random.random()
        if r < 0.1:
            sDate = row[0]
            s = random.choice(symbols)
            i = random.randint(0, len(sDate)-1) # индекс меняемого символа
            row[0] = sDate[:i] + s + sDate[i+1:]

    writer.writerow(row)

F.close()
