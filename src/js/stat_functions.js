// global variables {{{1
var rankTypes = {scale:1, bool:1};
var circTypes = {circ:1, circ_cat:1, time:1};
var deg2rad = Math.PI / 180;
var rad2deg = 180 / Math.PI;

//function Student(p, f) {{{1
function Student(p, f) {
  if (f > 200) {f = 200;};
  return student[f][p];
}

//function sortNumbers(a,b) {{{1
function sortNumbers(a,b) {
  return a-b;
}

//function Rank(X) {{{1
function Rank(X) {
  // Возвращает ранги X, связки не используются
  var XSorted = X.slice().sort(sortNumbers);
  var ranks = [];
  for (var i=0, l=X.length; i<l; i++) {
    var v = X[i];
    var firstIndex = XSorted.indexOf(v) + 1;
    var lastIndex = XSorted.lastIndexOf(v) + 1;
    var rank = (firstIndex + lastIndex) / 2;
    ranks.push(rank);
  }
  return ranks;
}

//function Significance(r,n) {{{1
function Significance(r,n) {
  // значимый или нет коэффициент корреляции r. n - величина выборки
  if (n < 10) {return false;}
  if (r === null) {return false;}

  r = Math.abs(r);
  var dof = n-1; // degrees of freedom
  var t = r * (Math.sqrt(dof) / Math.sqrt(1-r*r)) // http://matstats.ru/kr.html
  if (!isFinite(t)) {return true;} // r===1||r===-1
  var t099 = Student(0.01, dof);
  if (t > t099) {return true;}
  else {return false;}
}

//function CorrScale(r) {{{1
function CorrScale(r) {
  // Определить степень тесноты корреляционной связи
  // (http://www.learnspss.ru/hndbook/glava15/cont1.htm)
  if (r === null) {return null;}
  r = Math.abs(r);
  if (r < 0.2) {return null;}
  else if (r < 0.5) {return 'weak';}
  else if (r < 0.7) {return 'medium';}
  else if (r < 0.9) {return 'high';}
  else if (r <= 1.0) {return 'very_high';}
  else {
    console.error('Unexpected r in CorrScale: r=' + r);
    return null;
  }
}

//function Pearson(X,Y) {{{1
function Pearson(X,Y) {
  // Коэффициент линейной корреляции Пирсона
  n = X.length;
  // Проверка n в функции Correlation
  var xSum=0, ySum=0, xSqrSum=0, ySqrSum=0, productSum=0, i=n;
  while (i--) {
    var x=X[i], y=Y[i];
    xSum += x;
    xSqrSum += x*x;
    ySum += y;
    ySqrSum += y*y;
    productSum += x*y;
  }
  var productSumMean = productSum / n;
  var xMean = xSum / n;
  var yMean = ySum / n;
  var xStdev = Math.sqrt((xSqrSum - n*xMean*xMean) / (n-1));
  var yStdev = Math.sqrt((ySqrSum - n*yMean*yMean) / (n-1));

  var r = (productSumMean - xMean*yMean) / (xStdev * yStdev);
  if (!isFinite(r)) {return null;} // xStdev===0||yStdev===0
  else {return r;}
}

//function Spearman(X,Y) {{{1
function Spearman(X,Y) {
  // Коэффициент корреляции рангов
  // Проверка длины массива в функции Correlation
  var x = Rank(X);
  var y = Rank(Y);
  return Pearson(x,y);
}

//function LinCirc(X,Y) {{{1
function LinCirc(X,Y) {
  /* Коэффициент корреляции между линейной переменной X и угловой переменной Y. Углы даны в градусах.
   * Формула: (см. множественная корреляция)
   * R²(x,θ) = (r(x,c)**2+r(x,s)**2-2*r(x,c)*r(x,s)*r(c,s)) / (1-r(c,s)**2), где
   * r(x,c)=corr(x,cosθ), r(x,s)=corr(x,sinθ), r(c,s)=corr(cosθ,sinθ)
   * http://www.amazon.com/Directional-Statistics-Kanti-V-Mardia/dp/0471953334 p.245
   */
  // Преобразовываем угловую переменную Y в две скалярные переменные: C и S.
  // Проверка длины массива в функции Correlation
  var C=[], S=[];
  for (var i=0,l=Y.length; i<l; i++) {
    var y = Y[i] * deg2rad;
    C.push(Math.cos(y));
    S.push(Math.sin(y));
  }
  var Rxc = Pearson(X,C);
  var Rxs = Pearson(X,S);
  var Rcs = Pearson(C,S);
  var R;
  if (Rxc===null || Rxs===null || Rcs===null) {R = null;}
  else {R = Math.sqrt((Rxc*Rxc+Rxs*Rxs-2*Rxc*Rxs*Rcs) / (1-Rcs*Rcs));}
  if (!isFinite(R)) {return null;} //Rcs===1
  else {return R;}
}

//function LinCircRank(X,Y) {{{1
function LinCircRank(X,Y) {
  // см. doc к функции LinCirc
  // В http://www.amazon.com/Directional-Statistics-Kanti-V-Mardia/dp/0471953334 p.247 представлен
  // другой метод, где угловые данные равномерно размазываются по окружности
  // Проверка длины массива в функции Correlation
  var x = Rank(X);
  return LinCirc(x,Y);
}

//function CircCirc(X,Y) {{{1
function CircCirc(T,P) {
  /* Вычисляет коэффициент корреляции между двумя угловыми переменными T(theta) и P(phi).
   * Формула: (см. множественная корреляция)
   * R² = [(rcc**2+rcs**2+rsc**2+rss**2) + 2*(rcc*rss+rcs*rsc)*r1*r2 - 2*(rcc*rcs+rsc*rss)*r2 - 2*(rcc*rsc+rcs*rss)*r1] / [2*(1-r1**2)*(1-r2**2)], где
   * rcc=corr(cosθ,cosϕ), rcs=corr(cosθ,sinϕ), rsc=corr(sinθ,cosϕ), rss=corr(sinθ,sinϕ), r1=corr(cosθ,sinθ), r2=corr(cosϕ,sinϕ)
   * Диапазон: [0,1]
   * http://www.amazon.com/Directional-Statistics-Kanti-V-Mardia/dp/0471953334 p.249
   */
  // Проверка длины массива в функции Correlation
  var TC=[], TS=[], PC=[], PS=[];
  for (var i=0,l=T.length; i<l; i++) {
    var t = T[i] * deg2rad;
    var p = P[i] * deg2rad;
    TC.push(Math.cos(t));
    TS.push(Math.sin(t));
    PC.push(Math.cos(p));
    PS.push(Math.sin(p));
  }
  var Rcc = Pearson(TC,PC);
  var Rcs = Pearson(TC,PS);
  var Rsc = Pearson(TS,PC);
  var Rss = Pearson(TS,PS);
  var R1 = Pearson(TC,TS);
  var R2 = Pearson(PC,PS);
  
  var RSqr = ((Rcc*Rcc+Rcs*Rcs+Rsc*Rsc+Rss*Rss) + 2*(Rcc*Rss+Rcs*Rsc)*R1*R2 - 2*(Rcc*Rcs+Rsc*Rss)*R2 - 2*(Rcc*Rsc+Rcs*Rss)*R1) / (2*(1-R1*R1)*(1-R2*R2));
  var R = Math.sqrt(RSqr);
  if (!isFinite(R)) {return null;} // R1===1||R2===0
  else {return R;}
}

//function Contingency(X,Y) {{{1
function Contingency(X,Y) {
  /* Вычисляет коэффицент контингенции: частный случай коэффициента Пирсона для пары признаков,
   * характеризующихся только двумя категориями.
   * Используем вариант с несмещёнными оценками стандартных отклонений
   * См. http://en.wikipedia.org/wiki/Phi_coefficient
   */
  var n = X.length;
  // Проверка длины массива в функции Correlation
  var N11=0, N10=0, N01=0, N00=0;
  for (var i=0; i<n; i++) {
    var x=X[i], y=Y[i];
    if (x===1 && y===1) {N11++;}
    else if (x===1 && y===0) {N10++;}
    else if (x===0 && y===1) {N01++;}
    else if (x===0 && y===0) {N00++;}
    else {console.error('Unexpected bool values: x='+x+', y='+y);}
  }
  var N1a = N11 + N10;
  var N0a = N01 + N00;
  var Na1 = N11 + N01;
  var Na0 = N10 + N00;

  var nonbias = (n-1)/n; // коэффицент несмещённости
  var phi = (N11*N00 - N10*N01) / Math.sqrt(N1a*N0a*Na0*Na1) * nonbias;
  if (!isFinite(phi)) {return null;} // что-то в правой части равно 0
  else {return phi;}
}

//function Correlation(propData1, propData2) {{{1
function Correlation(propData1, propData2) {
  /* Функция-обёртка, возвращает объект {value, type, significant, scale} */
  var type1 = propData1.type, type2 = propData2.type;
  var trend1 = propData1.trend, trend2 = propData2.trend;
  var X = [], Y = [];
  var r, rType;
  var i = trend1.length;
  while (i--) {
    var v1 = trend1[i], v2 = trend2[i];
    if (v1===null || v2===null) continue;
    X.push(v1);
    Y.push(v2);
  }

  // недостаточно данных
  if (X.length < 10) {
    return {value:null, type:'noData', significant:false, scale:null};
  }

  // вычисляем коэффициент корреляции
  if (circTypes[type1] && circTypes[type2]) {
    r = CircCirc(X,Y);
    rType = 'CircCirc';
  }
  else if (type1==='bool' && type2==='bool') {
    r = Contingency(X,Y);
    rType = 'BoolBool';
  }
  // в аргументах LinCirc вторым аргументом идут циркулярные данные
  else if (circTypes[type1]) {
    if (rankTypes[type2]) {
      r = LinCircRank(Y,X);
      rType = 'LinCircRank';
    }
    else {
      r = LinCirc(Y,X);
      rType = 'LinCirc';
    }
  }
  else if (circTypes[type2]) {
    if (rankTypes[type1]) {
      r = LinCircRank(X,Y);
      rType = 'LinCircRank';
    }
    else {
      r = LinCirc(X,Y);
      rType = 'LinCirc';
    }
  }
  else {
    if (rankTypes[type1] || rankTypes[type2]) {
      r = Spearman(X,Y);
      rType = 'Spearman';
    }
    else {
      r = Pearson(X,Y);
      rType = 'Pearson';
    }
  }

  var significant = Significance(r, X.length);
  var scale = CorrScale(r);

  return {value:r, type:rType, significant:significant, scale:scale};
}

//function Regression(X, Y) {{{1
function Regression(X, Y) {
  // Вычисляет параметры уравнения регрессии и возвращает массивы точек тренда и
  // доверительных кривых (p=0.95)
  // Проверка адекватности исходных данных
  if (X.length != Y.length) {
    throw "arrays not equal";
  };
  n = X.length;
  if (n < 2) {
    throw "not enough data";
  };
  // Вычисление необходимых статистик
  var xSum = 0,
      xSqrSum = 0,
      ySum = 0,
      ySqrSum = 0,
      productSum = 0;
  for (var i=0; i<n; i++) {
    var x = X[i],
        y = Y[i];
    xSum += x;
    xSqrSum += x*x;
    ySum += y;
    ySqrSum += y*y;
    productSum += x*y;
  }
  var productSumMean = productSum / n;
  var xMean = xSum / n;
  var yMean = ySum / n;
  var xDiffSqrSum = xSqrSum - n*xMean*xMean; // для расчёта доверительных кривых
  var xStdev = Math.sqrt( xDiffSqrSum / (n-1) );
  var yStdev = Math.sqrt( (ySqrSum - n*yMean*yMean) / (n-1) );

  var b = (productSumMean - xMean * yMean) / (xStdev * xStdev);
  var a = yMean - b*xMean;
  /*
   * Расчёт линии регрессии
   */
  // находим стандартное отклонение регрессии (http://math.semestr.ru/corel/zadacha1.php)
  var yDiffSqrSum = 0,
      regrLine = []; // данные для линии регрессии
  for (var i=0; i<n; i++) {
    var Yx = b*X[i] + a;
    regrLine.push( [X[i],Yx] );
    var yDiffSqr = (Y[i]-Yx)*(Y[i]-Yx);
    yDiffSqrSum += yDiffSqr;
  }
  var f = n-3; // количество степеней свободы
  var Sy = Math.sqrt(yDiffSqrSum / f);
  // критерии стьюдента 
  var t = Student(0.05, f); // для линии регрессии
  var t1 = Student(0.1, f); // для значений
  // вычисляем доверительные интервалы для линии регрессии (http://people.stfx.ca/bliengme/ExcelTips/RegressionAnalysisConfidence2.htm)
  //и значений (http://math.semestr.ru/corel/prim.php)
  // данные для четырёх графиков: 2х снизу и 2х сверху тренда
  var regrLineConfBottom = [],
      regrLineConfTop = [],
      valuesConfBottom = [],
      valuesConfTop = [];
  for (var i=0; i<n; i++) {
    var Yx = regrLine[i][1];
    var regrLineDelta = t * Sy * Math.sqrt(1/(n-1) + ((X[i]-xMean)*(X[i]-xMean) / xDiffSqrSum));
    var valuesDelta = t1 * Sy;
    regrLineConfBottom.push([X[i], Yx-regrLineDelta]);
    regrLineConfTop.push([X[i], Yx+regrLineDelta]);
    valuesConfBottom.push([X[i], Yx-valuesDelta]);
    valuesConfTop.push([X[i], Yx+valuesDelta]);
  };
  function confSort(a,b) {
    if (a[0] == b[0]) {
      return a[1]-b[1]
    }
    else {
      return a[0]-b[0]
    }
  }
  regrLine.sort(confSort);
  regrLineConfBottom.sort(confSort);
  regrLineConfTop.sort(confSort);
  valuesConfBottom.sort(confSort);
  valuesConfTop.sort(confSort);

  return {
    'regrLine': regrLine,
    'regrLineConfBottom': regrLineConfBottom,
    'regrLineConfTop': regrLineConfTop,
    'valuesConfBottom': valuesConfBottom,
    'valuesConfTop': valuesConfTop
  } 
};

//function GetPoints(min, max, k, type) {{{1
function GetPoints(min, max, k, type) {
  var points = [];
  var h = (max-min) / k; // ширина интервала
  for (var i=0; i<=k; i++) {
    points.push(min + i*h);
  };
  // до скольки знаков округлять
  var fixed = -1 * (Math.floor(Math.log(h) / Math.log(10)) - 1);
  var factor = Math.pow(10, fixed);
  // округление значений точек
  points = points.map(function(x) {
    var value = Math.round(x*factor) / factor;
    // если все значения целые, все границы д.б. целые
    if (type == 'int') {
      if (value % 1 !== 0) {
        value = Math.round(value);
      };
    };
    return value;
  });
  // фиксим, если из-за округления min и/или max не попали
  var fix = Math.pow(10,-fixed);
  if (points[0] > min) {
    points[0] -= fix;
    points[0] = Math.round(points[0]*factor) / factor; // во избежание случаев 5.6000...0005
  };
  if (points[points.length-1] < max) {
    points[points.length-1] += fix; 
    points[points.length-1] = Math.round(points[points.length-1]*factor) / factor; // во избежание случаев 23.4000...0002
  };

  return points;
};

//function floor_to_number_in_array(n, arr, arr_sorted) {{{1
function floor_to_number_in_array(n, arr, arr_sorted) {
  if (!arr_sorted) {
    arr = arr.sort(function(a,b){return a-b;});
  };
  for (var i=arr.length; i--;) {
    if (arr[i] < n) {
      return arr[i];
    };
  };
  return arr[0];
};


//function GetBars(P) {{{1
function GetBars(P) {
  // Функция, возвращающая величины и интервалы(категории) столбцов для графика распределения
  //(гистограмма или роза)
  var barsType = 'categories'; // столбцы по категориям (по-умолчанию), второй - "intervals"
  var points = [];
  var values = P.values;
  
  if (P.type === 'bool') {
    var bars = {};
    bars[_('Истина')] = 0;
    bars[_('Ложь')] = 0;
    var i = values.length;
    while (i--) {
      if (values[i] === 1) {bars[_('Истина')]++;}
      else {bars[_('Ложь')]++;};
    };
    return bars;
  }
  else if (P.type === 'circ_cat') {
    //TODO: % штиля тоже д. показываться
    var inc = 100 / values.length; // инкремент в %
    var bars = {};
    var cats = P.maps.categories
    for (var i=0; i<cats.length; i++) {
      bars[cats[i]] = 0;
    };
    for (var i=0; i<values.length; i++) {
      var cat = P.maps.angle_cat[values[i].toFixed(1)];
      bars[cat] += inc;
    };
    // округление до 2 знаков
    for (var i=0; i<cats.length; i++) {
      var cat = cats[i];
      bars[cat] = Math.round(bars[cat]*100) / 100;
    };
    return bars;
  }
  else if (P.type === 'circ') {
    var inc = 100 / values.length; // инкремент в %
    var bars = {};
    // Количество столбцов
    var kArray = [2,3,4,5,6,8,9,10,12,15,18,20,24,30,36,40,45,60,72,90,120,180,360];
    var k = floor_to_number_in_array(Math.sqrt(values.length), kArray, true);
    var step = 360/k;
    P.cat_step = step;
    for (var i=0; i<k; i++) {
      key = 360/k*i;
      bars[key] = 0;
    };
    for (var i=0; i<values.length; i++) {
      var bar = Math.floor(values[i]/step) * step;
      if (bar === 360) {
        bar = 360 - step;
      };
      bars[bar] += inc;
    };
    // округление до 2 знаков
    for (var key in bars) {
      bars[key] = Math.round(bars[key]*100) / 100;
    };
    return bars;
  }
  else if (P.type === 'time') {
    var inc = 100 / values.length; // инкремент в %
    var bars = {};
    for (var i=0; i<24; i++) {
      bars[i] = 0;
    };
    var i = values.length;
    while (i--) {
      var hour = ~~(values[i]/15); // ~~ - округление вниз
      bars[hour] += inc;
    };
    // округление до 2 знаков
    for (var i=0; i<24; i++) {
      bars[i] = Math.round(bars[i]*100) / 100;
    };
    return bars;
  }
  // если параметр шкаловый, то столбцы - это ВСЕ градации
  else if (P.type === 'scale') {
    var scaleAttrs = P.scaleAttrs;
    for (var i=scaleAttrs[0]; i<=scaleAttrs[1]; i+=scaleAttrs[2]) {
      points.push(i);
    };
  }
  else { // int, float
    // min и max у параметра д.б. определены
    var min = P.stat.min;
    var max = P.stat.max;
    // Количество столбцов
    var k = Math.floor(Math.sqrt(values.length));
    // если все значения одинаковы, то точка одна
    if (min === max) {
      points.push(min);
    }
    else {
      var R = max - min;
      if (P.type === 'int') {
        // если размах (R) меньше k, то точки - целые числа от min до max
        if (R <= k) {
          for (var i=min; i<=max; i++) {
            points.push(i);
          }
        }
        else {
          points = GetPoints(min, max, k, 'int');
          barsType = 'intervals';
        }
      }
      else { // float
        points = GetPoints(min, max, k);
        barsType = 'intervals';
      };
    };
  };

  // По точкам вычисляем параметры столбцов
  // Столбцы по категориям
  if (barsType === 'categories') {
    var bars = {};
    for (var i=0; i<points.length; i++) {
      bars[points[i]] = 0;
    }
    var i = values.length;
    while (i--) {
      bars[values[i]]++;
    }
  }
  // Столбцы по интервалам
  else {
    var bars = {
      points: points,
      data: []
    };
    for (var i=0; i<points.length-1; i++) {
      bars.data.push([i+0.5, 0]);
    };
    // добавляем значения
    var i = values.length;
    while (i--) {
      var j = values.length-1;
      while (j--) {
        if (j === 0) { // первый диапазон [̲point1, point2]
          if (values[i] >= points[j] && values[i] <= points[j+1]) {
            bars.data[j][1]++;
          }
        }
        else { // последующие диапазоны (̲point1, point2]
          if (values[i] > points[j] && values[i] <= points[j+1]) {
            bars.data[j][1]++;
          }
        }
      }
    }
  }
  return bars;
}
