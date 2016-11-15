#coding: utf-8

"""На данный момент скрипт принимает в качестве аргумента файл с населёнными пунктами и определяет,
есть ли в нём повторяющиеся названия.
"""

import csv
from collections import Counter

def duplicates_exist(f):
    F = open(f)
    localities = []
    for row in csv.reader(F, delimiter=';'):
        localities.append(row[0].decode('utf-8'))
    F.close()
    n_all = len(localities)
    n_uniq = len(set(localities))
    if n_all == n_uniq:
        return False
    else:
        return True

def print_duplicates(f):
    F = open(f)
    localities = []
    for row in csv.reader(F, delimiter=';'):
        localities.append(row[0].decode('utf-8'))
    F.close()
    C = Counter(localities)
    duplicates = []
    for locality, n in C.iteritems():
        if n > 1:
            duplicates.append(locality)
    if not duplicates:
        print u"В файле %s нет повторов" % f
    else:
        print u"В файле %s повторяются населённые пункты:"
        for duplicate in duplicates:
            print duplicate


if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    if duplicates_exist(f):
        print_duplicates(f)
    else:
        print u"В файле %s повторов не обнаружено" % f
