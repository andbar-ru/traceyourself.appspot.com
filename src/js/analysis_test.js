//Схема DATA после отработки функции handleFile {{{1
/*
{
  dates: Array, // function buildData, список дат в формате iso в порядке, представленном в csv-файле (2012-01-01), length = <кол-во строк в csv-файле> - 1
  minDate: Number, // function buildData, минимальная дата из массива dates, value = new Date(date).valueOf()
  maxDate: Number, // function buildData, максимальная дата из массива dates, value = new Date(date).valueOf()
  uPropsOrder: Array, // function buildData, список пользовательских параметров в порядке, указанным в заголовке csv-файла, length = кол-во показателей.
  uProps: {
    propName: { // для каждого пользовательского параметра
      repr: String, // function buildData, html-представление параметра (propName)
      type: String, // function buildData, тип значений
      trend: Array, // function buildData, массив всех значений параметра, в том числе и пустые, в порядке, представленном в csv-файле, trend.length == dates.length
      values: Array, // function buildData, массив НЕПУСТЫХ значений параметра, используется при расчёте статистических показателей рядов и при построении некоторых видов графиков
      stat: { // function calcStat
        n: Number, // количество непустых значений
        min: Number, // минимальное значение из values
        max: Number, // максимальное значение из values
        mean: Number, // среднее значение из values
        stdev: Number // стандартное отклонение значений из values
      },
      phrase: String || Array // function buildPhrases, строка, массив или двумерный массив
    }
  },
  test: true,
  corrMatrix: { // function calcCorr
    rowPropname: { // для каждого пользовательского параметра
      colPropname: { // для каждого другого пользовательского параметра
        value: Number, // коэффициент корреляции
        type: String, // тип коэффициента корреляции
        significant: Bool, // значимость коэффициента корреляции
        scale: [null, 'weak', 'medium', 'high', 'very_high'] // степень тесноты связи
      }
    }
  }
}
*/

//global variables {{{1
var DATA = {}; // определяется в buildData

//function resetAnalysis() {{{1
//Обнуление из предыдущего анализа того, что не заменится в функции handleFile
function resetAnalysis() {
  $I('analysis').className = 'hidden';
  // Очистка глобальных переменных
  DATA = {};
  chartCbsChecked = [];
  // Скрытие таблиц и графиков
  var btns = [$I('toggleChart'), $I('toggleStattable'), $I('toggleCorrtable'), $I('toggleDatatable')];
  for (var i=0; i<btns.length; i++) {
    if (btns[i].className === 'active') {btns[i].click();}
  }
  // Скрытие форм
  var btns = $C('propsSelect');
  for (var i=0; i<btns.length; i++) {
    if (btns[i].innerHTML.indexOf(_('Скрыть')) !== -1) {btns[i].click();}
  }
  // Очистка графика
  $I('chartContainer').innerHTML = '';
}
//function validateDate(date) {{{1
// Проверка даты
function validateDate(date) {
  var dateRe = /^(\d{2}).(\d{2}).(\d{4})$/, // разделитель м.б. любой
      aDate = dateRe.exec(date);
  if (aDate === null) {
    return [false, _('Дата должна быть представлена в формате <b>дд.мм.гггг</b>')];
  }
  else {
    var d = aDate[1],
        m = aDate[2],
        y = aDate[3],
        D = new Date(y, m-1, d);
    if (D.getFullYear()!=y || D.getMonth()+1!=m || D.getDate()!=d) {
      return [false, _('Некорректная дата, такой даты скорее всего не существует')];
    }
    else {
      return [true, aDate[3]+'-'+aDate[2]+'-'+aDate[1]];
    }
  }
}

//function validateInt(v) {{{1
// Проверка целого числа
function validateInt(v) {
  var value = parseInt(v);
  if (!isNaN(value)) {
    return [true, value];
  }
  else {
    return [false, v+_(' не является целым числом')];
  }
}

//function validateFloat(v) {{{1
// Проверка числа с плавающей точкой
function validateFloat(v) {
  var value = parseFloat(v)
  if (!isNaN(value)) {
    return [true, value];
  }
  else {
    return [false, v+_(' не является числом с плавающей точкой')];
  }
}

//function validateBool(v) {{{1
// Проверка булева значения
function validateBool(v) {
  var trueValids = ['true', '1', '+', 'да'],
      falseValids = ['false', '0', '-', 'нет'];
  if (trueValids.indexOf(v) !== -1) {
    return [true, 1];
  }
  else if (falseValids.indexOf(v) !== -1) {
    return [true, 0];
  }
  else {
    return [false, _('В качестве булевых значений поддерживаются только: ') + trueValids.join(', ') + ', ' + falseValids.join(', ')];
  }
}

//function validateScale(v, validValues) {{{1
// Проверка шкалового значения
function validateScale(v, validValues) {
  var value = parseInt(v);
  if (!isNaN(value)) {
    if (validValues.indexOf(value) === -1) {
      return [false, v+_(' не входит в число допустимых значений: [')+validValues.join(',')+']'];
    }
    else {
      return [true, value];
    }
  }
  else {
    return [false, v+_(' не является целым числом')];
  }
}

//function validateTime(v) {{{1
// Проверка значения времени
function validateTime(v) {
  var timeRe = /([01][0-9]|2[0-3]):([0-5][0-9])/;
  var aTime = timeRe.exec(v);
  if (aTime === null) {
    return [false, _('Время должно быть представлено в формате ЧЧ:ММ и быть допустимым')];
  }
  else {
    // перевод в градусы
    var hh = parseInt(aTime[1]);
    var mm = parseInt(aTime[2]);
    var value = (hh*60 + mm) * 0.25;
    return [true, value];
  }
}

//function validateRange(range) {{{1
// Проверка диапазона при типе scale. Возвращает [true|false, valid_values|error]
function validateRange(range) {
  var rangeRe = /^\[(-?\d+),(-?\d+)(,(-?\d+))?\]$/,
      isValid = false,
      error = '';
  var aRange = rangeRe.exec(range);
  if (!aRange) {
    error = _('Диапазон шкалы задаётся в формате [<число>,<число>[,<шаг>]], например [0,10] или [-10,10,2]');
  }
  else {
    var from = parseInt(aRange[1]),
        to = parseInt(aRange[2]),
        step = parseInt(aRange[4]),
        max_gradation_count = 100;
    if (isNaN(step)) {
      if (to < from) {
        step = -1;
      }
      else {
        step = 1;
      }
    }
    if (step > 0 && from > to) {
      error = _('При положительном шаге число "от" должно быть меньше числа "до"');
    }
    else if (step < 0 && from < to) {
      error = _('При отрицательном шаге число "от" должно быть больше числа "до"');
    }
    else if (from === to) {
      error = _('Числа "от" и "до" не должны быть равны');
    }
    else if (step === 0) {
      error = _('Шаг не должен равняться 0');
    }
    else if ((to-from)/step > max_gradation_count) {
      var gradation_count = Math.ceil((to-from)/scale_step);
      error = _('Количество градаций в шкале не должно превышать ') + max_gradation_count + _(' у вас ') + gradation_count;
    }
    else if ((to-from)%step !== 0) {
      var gradation_count = (to - from) / step;
      error = _('Шаг должен помещаться в диапазон от ') + from + _(' до ') + to + _(' целое количество раз, у вас ') + gradation_count;
    }
    else {
      isValid = true;
    }
  }

  if (isValid === true) {
    return [true, [from, to, step]];
  }
  else {
    return [false, error];
  }
}

//function buildData(arrays) {{{1
// Создание DATA и проверка CSV-данных, представленных в виде массива массивов
function buildData(arrays) {
  /* Проверки:
   *  Количество колонок должно быть одинаково;
   *  Формат даты должен быть дд.мм.гггг;
   *  Даты не должны повторяться;
   *  Названия параметров не должны повторяться;
   *  Типы должны быть из списка поддерживаемых;
   *  Если есть тип 'scale', то диапазон должен быть правильный;
   *  Значения в колонках должны соответствовать своему типу или пустому значению;
   */
  DATA = {dates:[], uPropsOrder:[], uProps:{}, test:true};
  var header = arrays[0];
  var headerErrors = [];
  var colErrors = [];
  var typeErrors = [];
  var dateErrors = [];
  var validTypes = ['int', 'float', 'bool', 'scale', 'time'];
  var types = ['date'];

  // Проверка заголовка
  for (var i=1; i<header.length; i++) {
    var aProp = header[i].split(',');
    var name, type;
    if (aProp.length > 1) {
      name = aProp[0].trim();
      type = aProp[1].trim();
      if (type === 'scale') {
        if (aProp.length > 2) {
          var range = aProp.slice(2).join(',').split(' ').join('');
          var result = validateRange(range);
          if (result[0] !== true) {
            headerErrors.push([_('Неправильный диапазон ')+range, header[i], result[1]]);
          }
          else {
            var scaleAttrs = result[1];
          }
        }
        else {
          headerErrors.push([_('не указан диапазон при типе scale'), header[i], _('Диапазон шкалы задаётся в формате [<число>,<число>[,<шаг>]], например [0,10] или [-10,10,2]')]);
        }
      }
    }
    else {
      name = aProp[0].trim();
      type = 'float';
    }
    if (DATA.uProps[name]) {
      headerErrors.push([_('Одинаковые названия параметров: ')+name, header[i], _('Названия параметров не должны повторяться')]);
    }
    else if (validTypes.indexOf(type) === -1) {
      headerErrors.push([_('Неизвестный тип ')+type, header[i], _('Поддерживаются только типы: int, float, bool, scale, time')]);
    }
    else {
      var prop = {repr:name, trend:[], values:[]};
      if (type === 'scale') {
        var validValues = [];
        var curValue = scaleAttrs[0];
        while (curValue <= scaleAttrs[1]) {
          validValues.push(curValue);
          curValue += scaleAttrs[2];
        }
        types.push([type, validValues]);
        prop.scaleAttrs = scaleAttrs;
      }
      else {
        types.push(type);
      }
      prop['type'] = type;
      DATA.uPropsOrder.push(name);
      DATA.uProps[name] = prop;
    }
  }
  // Обработка ошибок
  if (headerErrors.length > 0) {
    var html = _('Ошибка в заголовке csv-файла!<br/>');
    html += '<table><tr><th>Ошибка</th><th>'+_('Показатель с ошибкой')+'</th><th>'+_('Пояснение')+'</th></tr>';
    for (var i=0; i<headerErrors.length; i++) {
      var e = headerErrors[i];
      html += '<tr><td>' + e[0] + '</td><td>' + e[1] + '</td><td>' + e[2] + '</td></tr>';
    }
    $I('warning').innerHTML = html;
    return false;
  }

  // Проверка и заполнение данных
  var hl = header.length;
  for (var i=1; i<arrays.length; i++) {
    var row = arrays[i];
    // Проверка количества столбцов
    var rl = row.length;
    if (rl !== hl) {
      colErrors.push([i+1, rl]);
    }
    else {
      // Проверка значений на соответствие типу
      for (var j=0; j<row.length; j++) {
        var value = row[j].split(' ').join(''),
            type = types[j],
            result = [true, null],
            typeInTd = '';
        if (type === 'date') {
          result = validateDate(value);
          typeInTd = _('Дата');
        }
        else {
          if (value !== '' && value !== '--') {
            if (type === 'int') {
              result = validateInt(value);
              typeInTd = _('Целое число');
            }
            else if (type === 'float') {
              result = validateFloat(value);
              typeInTd = _('Число с плавающей точкой');
            }
            else if (type === 'bool') {
              result = validateBool(value);
              typeInTd = _('Булево');
            }
            else if (type instanceof Array && type[0] === 'scale') {
              result = validateScale(value, type[1]);
              typeInTd = _('Шкала');
            }
            else if (type === 'time') {
              result = validateTime(value);
              typeInTd = _('Время');
            }
            else { // Это никогда не должно выполняться
              result = [false, _('Неизвестный тип')];
              typeInTd = type;
            }
          }
          else { result = [true, null]; }
        }
        if (result[0] === true) {
          if (type === 'date') {
            var d = result[1];
            // Проверка даты на уникальность
            var index = DATA.dates.indexOf(d);
            if (index !== -1) {
              dateErrors.push([i+1, d, index+2]);
            }

            DATA.dates.push(d);
            d = new Date(result[1]).getTime();
            if (DATA.minDate === undefined || d < DATA.minDate) {
              DATA.minDate = d;
            }
            if (DATA.maxDate === undefined || d > DATA.maxDate) {
              DATA.maxDate = d;
            }
          }
          else {
            // Заполнение данных
            var propData = DATA.uProps[DATA.uPropsOrder[j-1]];
            propData.trend.push(result[1]);
            if (result[1] !== null) { propData.values.push(result[1]); }
          }
        }
        else { typeErrors.push([i+1, value, typeInTd, result[1]]); }
      }
    }
  }
  // Обработка ошибок
  if (colErrors.length > 0) {
    var html = _('Ошибка формата csv - количество столбцов неодинаково!<br/>');
    html += _('Количество столбцов в строках должно быть <b>') + hl + _('</b> (количество столбцов в заголовке).');
    html += _('Иное количество столбцов в следующих строках:');
    html += '<table><tr><th>'+_('Номер строки')+'</th><th>'+_('Количество столбцов')+'</th></tr>';
    for (var i=0; i<colErrors.length; i++) {
      var e = colErrors[i];
      html += '<tr><td>' + e[0] + '</td><td>' + e[1] + '</td></tr>';
    }
    $I('warning').innerHTML = html;
    return false;
  }
  else if (typeErrors.length > 0) {
    var html = _('Ошибка в формате данных!<br/>');
    html += _('Значения не соответствуют заявленному типу в следующих строках:');
    html += '<table><tr><th>'+_('Номер строки')+'</th><th>'+_('Значение')+'</th><th>'+_('Тип')+'</th><th>'+_('Ошибка')+'</th></tr>';
    for (var i=0; i<typeErrors.length; i++) {
      var e = typeErrors[i];
      html += '<tr><td>'+e[0]+'</td><td>'+e[1]+'</td><td>'+e[2]+'</td><td>'+e[3]+'</td></tr>';
    }
    $I('warning').innerHTML = html;
    return false;
  }
  else if (dateErrors.length > 0) {
    var html = _('Встречаются повторы в датах!<br/>');
    html += _('Дублируются даты в следующих строках:');
    html += '<table><tr><th>'+_('Номер строки')+'</th><th>'+_('Дата')+'</th><th>'+_('Номер строки, с которой совпадает')+'</th></tr>';
    for (var i=0; i<dateErrors.length; i++) {
      var e = dateErrors[i];
      html += '<tr><td>'+e[0]+'</td><td>'+e[1]+'</td><td>'+e[2]+'</td></tr>';
    }
    $I('warning').innerHTML = html;
    return false;
  }
  else {
    return DATA;
  }
};

//function handleFile(file) {{{1
// Обработка CSV-файла
function handleFile(file) {
  var reader = new FileReader();
  reader.onload = function(event) {
    console.time('handleFile');
    var content = event.target.result;
    var arrays = $.csv.toArrays(content, {separator: ';'});
    console.time('buildData');
    var result = buildData(arrays);
    console.timeEnd('buildData');
    if (result !== false) {
      // Статистические показатели
      for (var prop in DATA.uProps) {
        calcStat(DATA.uProps[prop]);
      }
      calcCorr();
      buildForms();
      buildTables();
      buildDefaultChart();
      buildPhrases();
      buildSummary();
      // Схема DATA в начале файла
      $I('analysis').classList.remove('hidden');
    }
    $I('wait').innerHTML = '';
    console.timeEnd('handleFile');
  }

  reader.onerror = function(event) {
    console.error("File could not be read! Code " + event.target.error.code);
  };

  reader.readAsText(file);
}

$(document).ready(function() { //{{{1
  //$I('fileSelect').onclick = function() {{{2
  // Загрузка данных
  $I('fileSelect').onclick = function() {
    $I('file').click();
  }

  $I('file').onchange = function(e) { //{{{2
    resetAnalysis();
    
    var file = e.target.files[0],
        warnDiv = $I('warning'),
        fileSpan = $I('fileSelected');
    if (file) {
      if (file.type !== 'text/csv' && file.type !== 'text/comma-separated-values') {
        warnDiv.innerHTML = _('Принимаются только файлы в формате csv.');
      }
      else if (file.size > 102400) {
        warnDiv.innerHTML = _('Размер файла превышает 100 кб.'); 
      }
      else {
        fileSpan.innerHTML = file.name;
        warnDiv.innerHTML = '';
        $I('wait').innerHTML = _('Подождите, идёт загрузка и обработка данных.');
        handleFile(file);
      }
    }
    else {
      fileSpan.innerHTML = _('файл не выбран');
    }
  };

  // Pager {{{2
  pagerToggle();

  //Кнопка "Скрыть/Показать инструкции" {{{2
  $I('toggleInstructions').onclick = function() {
    var E = $I('instructions');
    if (E.className === 'hidden') {
      E.className = '';
      this.innerHTML = _('Скрыть инструкции');
    }
    else {
      E.className = 'hidden';
      this.innerHTML = _('Показать инструкции');
    }
  }
  
  // Обработчики кликов по кнопкам {{{2
  // Показать|Скрыть форму
  var btns = $C('propsSelect');
  for (var i=0; i<btns.length; i++) {
    btns[i].onclick = toggleForm;
  }
  $I('toggleDatatable').onclick = toggleDatatable;
  $I('toggleStattable').onclick = toggleStattable;
  $I('toggleCorrtable').onclick = toggleCorrtable;
  $I('toggleChart').onclick = toggleChart;
  //Представление таблиц в отдельном окне
  var btns = $C('tablePopup');
  var i = btns.length;
  while (i--) {
    btns[i].onclick = tablePopup;
  }
  // Скачивание таблиц
  $I('datatable2csv').onclick = function() {table2file('dataTable', 'csv');};
  $I('stattable2csv').onclick = function() {table2file('statTable', 'csv');};
  $I('corrtable2csv').onclick = function() {table2file('corrTable', 'csv');};
  $I('stattable2xlsx').onclick = function() {table2file('statTable', 'xlsx');};
  $I('corrtable2xlsx').onclick = function() {table2file('corrTable', 'xlsx');};
  $I('datatable2xlsx').onclick = function() {table2file('dataTable', 'xlsx');};
});
//}}}
