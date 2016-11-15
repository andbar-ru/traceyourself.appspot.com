#coding: utf-8

"""
В этом модуле располагаются функции, необходимые для статистических расчётов
"""

import math
import logging
from student_tables import student099

def Rank(X):
    """Возвращает ранги X, связки не используем"""
    X_sorted = sorted(X)
    ranks = []
    for x in X:
        count = X_sorted.count(x)
        first_index = X_sorted.index(x) + 1
        if count == 1:
            ranks.append(first_index)
        else:
            rank_mean = (2*first_index+count-1) / 2. # (first_index+last_index)/2
            ranks.append(rank_mean)

    return ranks


def Student099(f):
    """Значение критерия Стьюдента при p=0.99"""
    if f > 200:
        f = 200
    return student099[f]


def Significance(r, n):
    """Значимый или нет коэффициент корреляции r. n - величина выборки."""
    if n < 10:
        return False
    if r is None:
        return False

    r = abs(r)
    dof = n-2 # degrees of freedom
    try:
        t = r * (dof**0.5 / (1-r**2)**0.5) # http://matstats.ru/kr.html
        t099 = Student099(dof)
        if t > t099:
            return True
        else:
            return False
    except ZeroDivisionError:
        return True # r = 1 or -1


def Corr_scale(r):
    """Определить степень тесноты корреляционной связи
    (http://www.learnspss.ru/hndbook/glava15/cont1.htm)"""
    if r is None:
        return None

    r = abs(r)
    if r < 0.2:
        return None
    elif r < 0.5:
        return 'weak'
    elif r < 0.7:
        return 'medium'
    elif r < 0.9:
        return 'high'
    elif r <= 1.0:
        return 'very_high'
    else:
        logging.error("Unexpected r in corr_scale: r=%.4f" % r)
        return None


def Correlation(prop_data1, prop_data2):
    """Функция-обёртка.
    Вычисляет коэффициент корреляции между двумя параметрами
    prop_data1 и prop_data2 - словари, содержащие данные по параметрам (analysis.py)
    Если данных недостаточно (меньше 10), возвращается None.
    Возвращает словарь {value, type, significant, scale}.
    """
    type1 = prop_data1['type']
    type2 = prop_data2['type']
    trend1 = prop_data1['trend']
    trend2 = prop_data2['trend']
    # Убираем из трендов даты, по которым хотя бы в одном из трендов пустое значение.
    # Должны вернуться 2 одинаковых по размеру списка с непустыми значениями.
    # Значения по одинаковым индексам д.б. по одной дате (полагаемся на согласованность трендов)
    empty_values = (None, '')
    X = []
    Y = []
    for i in xrange(len(trend1)):
        value1, value2 = trend1[i], trend2[i]
        if value1 not in empty_values and value2 not in empty_values:
            X.append(value1)
            Y.append(value2)

    # недостаточно данных
    if len(X) < 10:
        corr = {'value':None, 'type':'no_data', 'significant':False, 'scale':None}
        return corr

    # вычисляем коэффициент корреляции
    if type1 in ('circ', 'circ_cat', 'time') and type2 in ('circ', 'circ_cat', 'time'):
        r = Circular_Circular(X,Y,radians=False)
        r_type = 'circ_circ'
    elif type1=='bool' and type2=='bool':
        r = Contingency(X,Y)
        r_type = 'bool_bool'
    # в аргументах lin_circ вторым аргументом идут циркулярные данные
    elif type1 in ('circ', 'circ_cat', 'time'):
        if type2 in ('scale', 'bool'):
            r = Linear_Circular_Rank(Y,X,radians=False)
            r_type = 'lin_circ_rank'
        else:
            r = Linear_Circular(Y,X,radians=False)
            r_type = 'lin_circ'
    elif type2 in ('circ', 'circ_cat', 'time'):
        if type1 in ('scale', 'bool'):
            r = Linear_Circular_Rank(X,Y,radians=False)
            r_type = 'lin_circ_rank'
        else:
            r = Linear_Circular(X,Y,radians=False)
            r_type = 'lin_circ'
    else:
        if type1 in ('scale','bool') or type2 in ('scale','bool'):
            r = Spearman(X,Y)
            r_type = 'spearman'
        else:
            r = Pearson(X,Y)
            r_type = 'pearson'

    r_significant = Significance(r, len(X))
    r_scale = Corr_scale(r)

    corr = {'value':r, 'type':r_type, 'significant':r_significant, 'scale':r_scale}
    return corr


def Pearson(X,Y):
    """Вычисляет коэффицент корреляции Пирсона.
    X и Y м.б. числовыми данными или рангами (Спирмена).
    X и Y д.б. одинаковой длины.
    Если данных меньше 10, то возвращаем None.
    Используем несмещённые оценки стандартного отклонения.
    """
    n = len(X)
    if n < 10:
        return None
    x_sum = y_sum = x_sqr_sum = y_sqr_sum = product_sum = 0
    for i in xrange(n):
        x = X[i]
        y = Y[i]
        x_sum += x
        x_sqr_sum += x*x
        y_sum += y
        y_sqr_sum += y*y
        product_sum += x*y
    n = float(n)
    product_sum_mean = product_sum / n
    x_mean = x_sum / n
    y_mean = y_sum / n
    x_stdev = ( (x_sqr_sum - n*x_mean*x_mean) / (n-1) )**0.5
    y_stdev = ( (y_sqr_sum - n*y_mean*y_mean) / (n-1) )**0.5
    try:
        r = (product_sum_mean - x_mean*y_mean) / (x_stdev*y_stdev)
    except ZeroDivisionError:
        r = None

    return r


def Spearman(X,Y):
    """Вычисляет коэффицент ранговой корреляции Спирмена.
    Так как могут встречаться повторы, то для рангов используется формула Пирсона.
    """
    # ранги
    x = Rank(X)
    y = Rank(Y)
    return Pearson(x,y)

def Contingency(X,Y):
    """Вычисляет коэффицент контингенции: частный случай коэффициента Пирсона для пары признаков,
    характеризующихся только двумя категориями.
    Используем вариант с несмещёнными оценками стандартных отклонений
    См. http://en.wikipedia.org/wiki/Phi_coefficient
    """
    n = len(X)
    N11 = N10 = N01 = N00 = 0
    for i in xrange(n):
        x = X[i]
        y = Y[i]
        if x==1 and y==1:
            N11 += 1
        elif x==1 and y==0:
            N10 += 1
        elif x==0 and y==1:
            N01 += 1
        elif x==0 and y==0:
            N00 += 1
        else:
            logging.error("Unexpected bool values: x=%s, y=%s" % (x, y))
    N1a = N11+N10
    N0a = N01+N00
    Na1 = N11+N01
    Na0 = N10+N00

    try:
        n = float(n)
        nonbias = (n-1)/n # коэффицент несмещённости
        phi = (N11*N00-N10*N01) / (N1a*N0a*Na0*Na1)**0.5 * nonbias
    except ZeroDivisionError:
        phi = None
    return phi


def Linear_Circular(X,As,radians=False):
    """Вычисляет коэффициент корреляции между линейной переменной X и угловой переменной As.
    radians: Углы As представлены в радианах (True) или градусах (False).
    Формула: (см. множественная корреляция)
    R²(x,θ) = (r(x,c)**2+r(x,s)**2-2*r(x,c)*r(x,s)*r(c,s)) / (1-r(c,s)**2), где
    r(x,c)=corr(x,cosθ), r(x,s)=corr(x,sinθ), r(c,s)=corr(cosθ,sinθ)
    http://www.amazon.com/Directional-Statistics-Kanti-V-Mardia/dp/0471953334 p.245
    """
    if radians == False:
        As = map(math.radians, As)
    # преобразовываем угловую переменную As в две скалярные переменные C и S
    C = map(math.cos, As)
    S = map(math.sin, As)
    Rxc = Pearson(X,C)
    Rxs = Pearson(X,S)
    Rcs = Pearson(C,S)
    try:
        R = ((Rxc**2+Rxs**2-2*Rxc*Rxs*Rcs) / (1-Rcs**2))**0.5
    except TypeError: # Pearson(?,?) = None
        R = None
    return R


def Linear_Circular_Rank(X,As,radians=False):
    """Вычисляет коэффициент корреляции между линейное переменной X и угловой переменной As.
    radians: Углы As представлены в радианах (True) или градусах (False).
    """
    # В http://www.amazon.com/Directional-Statistics-Kanti-V-Mardia/dp/0471953334 p.247 представлен
    # другой метод, где угловые данные размазываются равномерно по окружности
    x = Rank(X)
    return Linear_Circular(x,As,radians)


def Circular_Circular(T,P,radians=False):
    """Вычисляет коэффициент корреляции между двумя угловыми переменными T(theta) и P(phi).
    radians: Углы As представлены в радианах (True) или градусах (False).
    Формула: (см. множественная корреляция)
    R² = [(rcc**2+rcs**2+rsc**2+rss**2) + 2*(rcc*rss+rcs*rsc)*r1*r2 - 2*(rcc*rcs+rsc*rss)*r2 - 2*(rcc*rsc+rcs*rss)*r1] / [2*(1-r1**2)*(1-r2**2)], где
        rcc=corr(cosθ,cosϕ), rcs=corr(cosθ,sinϕ), rsc=corr(sinθ,cosϕ), rss=corr(sinθ,sinϕ), r1=corr(cosθ,sinθ), r2=corr(cosϕ,sinϕ)
    Диапазон: [0,1]
    http://www.amazon.com/Directional-Statistics-Kanti-V-Mardia/dp/0471953334 p.249
    """
    if radians == False:
        T = map(math.radians, T)
        P = map(math.radians, P)

    TC = map(math.cos, T)
    TS = map(math.sin, T)
    PC = map(math.cos, P)
    PS = map(math.sin, P)
    rcc = Pearson(TC,PC)
    rcs = Pearson(TC,PS)
    rsc = Pearson(TS,PC)
    rss = Pearson(TS,PS)
    r1 = Pearson(TC,TS)
    r2 = Pearson(PC,PS)

    R_sqr = ((rcc**2+rcs**2+rsc**2+rss**2) + 2*(rcc*rss+rcs*rsc)*r1*r2 - 2*(rcc*rcs+rsc*rss)*r2 - 2*(rcc*rsc+rcs*rss)*r1) / (2*(1-r1**2)*(1-r2**2))
    R = R_sqr**0.5

    return R


def circular_mean(As, radians=True):
    """Вычисляет средний угол для набора углов As.
    radians - углы даются в радианах. Если False, то в градусах.
    Если результат неопределён (S==C==0), возвращает None
    http://en.wikipedia.org/wiki/Mean_of_circular_quantities
    """
    if radians == False:
        As = map(math.radians, As)
    S = sum(map(math.sin, As))
    C = sum(map(math.cos, As))
    if round(S,10) == 0 and round(C,10) == 0:
        return None
    else:
        mean = math.atan2(S,C)
    # отрицательный угол в положительный
    if mean < 0:
        mean = mean + 2*math.pi

    if radians == False:
        return math.degrees(mean)
    return mean


def circular_stdev(As, radians=True):
    """Вычисляет стандартное отклонение для набора углов As.
    radians - углы даются в радианах. Если False, то в градусах.
    http://en.wikipedia.org/wiki/Statistics_of_non-Euclidean_spaces
    """
    if radians == False:
        As = map(math.radians, As)
    n = float(len(As))
    S = sum(map(math.sin, As))
    C = sum(map(math.cos, As))
    R = (C*C+S*S)**0.5
    R_mean = R / n
    stdev = (-2*math.log(R_mean))**0.5

    if radians == False:
        return math.degrees(stdev)
    return stdev
