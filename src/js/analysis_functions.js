// global variables {{{1
var deg2rad = Math.PI / 180;
var rad2deg = 180 / Math.PI;
var modelMap = {
  Indice: _('Индексы'),
  Commodity: _('Товары'),
  Currency: _('Валютные пары'),
  AstroData: _('Астрономические данные'),
  CommonData: _('Геомагнитные данные'),
  CommonCityData: _('Данные погоды')
}
var circTypes = {circ:1, circ_cat:1, time:1};
var scaleMap = {'weak':_('слабая'), 'medium':_('средняя'), 'high':_('сильная'), 'very_high':_('очень сильная')};
var chartCbsChecked = [];

//dateinput localization {{{1
$.tools.dateinput.localize("ru", {
  months: 'январь,февраль,март,апрель,май,июнь,июль,август,сентябрь,октябрь,ноябрь,декабрь',
  shortMonths: 'янв,фев,мар,апр,май,июн,июл,авг,сен,окт,ноя,дек',
  days: 'воскресенье,понедельник,вторник,среда,четверг,пятница,суббота',
  shortDays: 'вс,пн,вт,ср,чт,пт,сб'
});
var ruFormat = /(\d{2})\.(\d{2})\.(\d{4})/;
var enFormat = /(\d{2})\/(\d{2})\/(\d{4})/;

//function showOnlyOne(objId) {{{1
function showOnlyOne(objId) {
  for (var id in objButtMap) {
    if (id !== objId) {
      if (!$I(id).classList.contains('hidden')) {
        $I(objButtMap[id]).click();
      }
    }
  };
  $I(objId).classList.remove('hidden');
}

//Show|Hide tables|graph {{{1
// Кнопки показа графиков/таблиц. Если что-то одно показывается, остальные д.б. скрыты
var objButtMap = {
  'chartWrapper': 'toggleChart',  
  'stattableWrapper': 'toggleStattable', 
  'corrtableWrapper': 'toggleCorrtable', 
  'datatableWrapper': 'toggleDatatable' 
};

//function tablePopup() {{{1
// Представление таблиц в отдельном окне
function tablePopup() {
  var tableDiv = this.parentNode.nextElementSibling.nextElementSibling;
  var tableId = tableDiv.getElementsByTagName('table')[0].id;
  var tableHTML = tableDiv.innerHTML;
  var popup = window.open('', tableId);
  var popupHTML = '<!DOCTYPE html><html><head><meta charset="utf-8"/><link rel="stylesheet" href="/css/reset.css"/><link rel="stylesheet" href="/css/main.css"/><link rel="stylesheet" href="/css/analysis.css"/>';
  if (tableId === 'dataTable') {
    popupHTML += '<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>'+
      '<script src="/js/jquery.tablesorter.min.js"></script>'+
      '<script src="/js/tablesorter_extra.js"></script>'+
      '<script src="/js/jquery.tablesorter.pager.min.js"></script>'+
      '<script src="/js/jed.js"></script>'+
      '<script src="/js/locale/'+lang+'/messages.js"></script>'+
      '<script src="/js/udf.js"></script>'+
      '<script src="/js/analysis_datatable.js"></script>';
  }
  popupHTML += '<title>'+_('Таблица')+'</title></head><body>';
  if (tableId === 'dataTable') {
    popupHTML += '<p><button id="pagerToggle">'+_('Отключить разбиение на страницы')+'</button></p>';
  }
  popupHTML += tableHTML;
  if (tableId === 'dataTable') {
    popupHTML += '<script>datatableSort(); pagerToggle(); $I("pagerToggle").click();</script>'
  }
  popupHTML += '</body></html>';

  popup.document.open();
  popup.document.write(popupHTML);
  popup.document.close();

  return false;
}

//function formatDate(date) {{{1
// Русский формат даты
function formatDate(date) {
  var day = date.getDate(); if (day<10) {day='0'+day};
  var month = date.getMonth()+1; if (month<10) {month='0'+month};
  var year = date.getFullYear();
  return day+'.'+month+'.'+year;
}

//function formatTime(value) {{{1
// градусы -> чч:мм
function formatTime(value) {
  var mins = value * 4;
  var hours = ~~(mins/60);
  mins = Math.round(mins%60);
  if (mins === 60) {
    mins = 0;
    hours++;
  };
  if (hours === 24) {
    hours = 0;
  };
  return [hours, mins];
}

//function hhmm(hours) {{{1
function hhmm(hours) {
  var HH = parseInt(hours);
  if (HH < 10) {
    HH = "0" + HH;
  };
  var MM = Math.round(hours%1*60);
  if (MM < 10) {
    MM = "0" + MM;
  }
  return [HH,MM]
}

//function format(value, type) {{{1
function format(value, type, maps) {
  if (type === 'bool') {
    return value===1 ? _('Истина') : _('Ложь');
  }
  else if (type === 'time') {
    var hhmm = formatTime(value),
        hours = hhmm[0],
        mins = hhmm[1];
    if (hours < 10) {hours = '0'+hours};
    if (mins < 10) {mins = '0'+mins};
    return hours+':'+mins;
  }
  else if (type === 'circ_cat') {
    if (typeof value === 'number') {
      value = value.toFixed(1);
    };
    return maps['angle_repr'][value];
  }
  else if (type === 'duration') {
    var hours = ~~value;
    var mins = Math.round(value%1*60);
    if (mins === 60) {
      mins = 0;
      hours++;
    };
    if (hours === 24) {
      hours = 0;
    };
    return hours+_('ч ')+mins+_('мин');
  }
  else {
    return value;
  };
};

//function formatStat(value, statName, type, maps) {{{1
function formatStat(value, statName, type, maps) {
  if (value === null) {
    return value;
  };
  if (statName === 'n') {
    return value;
  }
  else if (statName==='min' || statName==='max') {
    if ({bool:1, time:1, duration:1}[type]) {
      return format(value, type);
    }
    else if (type === 'circ_cat') {
      return null;
    }
    else {
      return value;
    };
  }
  else if (statName==='mean') {
    if (type === 'bool') {
      var tip;
      if (value<0.5 && value>=0) {
        tip = _('Ложь');
      }
      else if (value>0.5 && value<=1) {
        tip = _('Истина');
      }
      else { // 0.5
        tip = '?';
      };
      return value.toFixed(2)+' ('+tip+')';
    }
    else if (type==='time' || type==='duration') {
      return format(value, type);
    }
    else if (type === 'circ_cat') {
      var closest_angle = (maps['angle_step'] * Math.round(value/maps['angle_step'])).toFixed(1);
      return Math.round(value) + '&deg; (' + maps['angle_repr'][closest_angle] + ')';
    }
    else {
      return value.toFixed(2);
    };
  }
  else if (statName === 'stdev') {
    if (type === 'time') {
      var hhmm = formatTime(value);
      var hours = hhmm[0];
      var mins = hhmm[1];
      return hours+_('ч ')+mins+_('мин');
    }
    else if (type === 'circ_cat') {
      return Math.round(value) + '&deg;';
    }
    else if (type === 'duration') {
      return format(value, type);
    }
    else {
      return value.toFixed(2);
    };
  }
  else {
    throw("Unknown statistics name:" + statName);
    return value;
  };
};

//function formatCorrTd(corr) {{{1
function formatCorrTd(corr) {
  var value = corr.value;
  var scale = corr.scale;
  if (value === null) {
    var content = '--';
  }
  else {
    var content = value.toFixed(2);
  };
  var class_ = '';
  if (corr.significant===true && scale!==null) {
    class_ = ' class="significant"';
  };
  if (scale==='medium' || scale==='high' || scale==='very_high') {
    class_ = ' class="'+scale+'"';
  }
  return '<td'+class_+'>'+content+'</td>';
}


//function propRepr(prop) {{{1
function propRepr(prop) {
  if (!isNaN(parseInt(prop)) || DATA.test===true) { // uProp
    var repr = DATA.uProps[prop].repr;
  } 
  else { // cProp
    var model = prop.split('.')[0];
    var repr = DATA.cProps[model][prop].repr;
  }

  return repr;
}


//function formatPhrase(phrase) {{{1
function formatPhrase(phrase) {
  var html = '';
  if (typeof(phrase) === 'string') {
    html = phrase;
  }
  else if (phrase instanceof Array) {
    if (typeof(phrase[0]) === 'string') {
      html += _('сильных связей с другими показателями нет')+'<br/>';
      html += _('самая сильная связь с показателем "')+propRepr(phrase[0])+'" (r = '+phrase[1].toFixed(2)+_(', связь ')+scaleMap[phrase[2]]+')';
    }
    else if (phrase[0] instanceof Array) {
      html += _('есть сильные связи с параметрами:');
      html += '<ul>';
      for (var i=0; i<phrase.length; i++) {
        var p = phrase[i];
        html += '<li>"'+propRepr(p[0])+'" (r = '+p[1].toFixed(2)+_(', связь ')+scaleMap[p[2]]+')</li>';
      }
      html += '</ul>';
    }
  }
  return html;
}
// function format4line(value, P) {{{1
function format4line(value, P) {
  if (value !== null) {
    if (P.type === 'circ_cat') {
      // значения по номеру категории
      if (value !== '') {
        var cat = P.maps.angle_cat[value.toFixed(1)];
        value = P.maps.categories.indexOf(cat);
      }
      else {
        value = null;
      };
    }
    else if (P.type === 'time') {
      value /= 15; // перевод градусов в часы
    }
    return value;
  }
  else {
    return null;
  }
}
//function calcStat(propData) {{{1
// Вычислить статистические показатели ряда 'values' и поместить их в свойство 'stat'
function calcStat(data) {
  data.stat = {n:null, min:null, max:null, mean:null, stdev:null};

  var type = data.type;
  var values = data.values;

  // количество
  var n = values.length;
  data.stat.n = n;

  if (n > 0) {
    var i=n, min=Infinity, max=-Infinity, sum=0, sumSqr=0, sumSin=0, sumCos=0, mean=null, stdev=null;
    while (i--) {
      var v = values[i];
      // минимум, максимум
      if (!{circ:1, circ_cat:1}[type]) {
        if (v < min) min = v;
        if (v > max) max = v;
      }
      // среднее и стандартное отклонение
      if ({scale:1, int:1, float:1, bool:1, duration:1}[type]) {
        sum += v;
        sumSqr += v*v;
        mean = sum / n;
        if (n > 1) {
          if (type === 'bool') {stdev = (n*mean*(1-mean)) / (n-1);}
          else {stdev = Math.sqrt((sumSqr-n*mean*mean) / (n-1));}
        }
      }
      else if ({time:1, circ:1, circ_cat:1}[type]) {
        sumSin += Math.sin(v*deg2rad);
        sumCos += Math.cos(v*deg2rad);
        if (sumSin.toFixed(10)*1 === 0 && sumCos.toFixed(10)*1 === 0) {
          mean = null;
        }
        else {
          mean = Math.atan2(sumSin, sumCos);
          if (mean < 0) { mean += 2*Math.PI }
          mean *= rad2deg;
        }
        if (n > 1) {
          var R = Math.sqrt(sumCos*sumCos + sumSin*sumSin);
          var RMean = R / n;
          stdev = Math.sqrt(-2*Math.log(RMean));
          stdev *= rad2deg;
        }
      }
    }

    data.stat.n = n;
    if (!{circ:1, circ_cat:1}[type]) {data.stat.min = min;}
    if (!{circ:1, circ_cat:1}[type]) {data.stat.max = max;}
    data.stat.mean = mean;
    data.stat.stdev = stdev;
  }
}

//function calcCorr() {{{1
// Вычислить корреляционную таблицу и поместить в свойство 'corrMatrix'
function calcCorr() {
  console.time('calcCorr');
  corrMatrix = {};
  // строки - общие параметры
  for (var rowModel in DATA.cProps) {
    var rowProps = DATA.cProps[rowModel];
    for (var rowProp in rowProps) {
      if (rowProp === 'propsOrder') continue;
      corrMatrix[rowProp] = {};
      rowPropData = rowProps[rowProp];
      // столбцы - общие параметры
      for (var colModel in DATA.cProps) {
        var colProps = DATA.cProps[colModel];
        for (var colProp in colProps) {
          if (colProp === 'propsOrder') continue;
          var colPropData = colProps[colProp];
          if (rowProp !== colProp) {
            if (colProp in corrMatrix) {
              corrMatrix[rowProp][colProp] = corrMatrix[colProp][rowProp];
            }
            else {
              corrMatrix[rowProp][colProp] = Correlation(rowPropData, colPropData);
            }
          }
        }
      }
      // столбцы - пользовательские параметры
      for (var colProp in DATA.uProps) {
        var colPropData = DATA.uProps[colProp];
        // общий параметр не может совпадать с пользовательским
        // пользовательских параметров ещё нет в corrMatrix
        corrMatrix[rowProp][colProp] = Correlation(rowPropData, colPropData);
      }
    }
  }
  // строки - пользовательские параметры
  for (var rowProp in DATA.uProps) {
    corrMatrix[rowProp] = {};
    var rowPropData = DATA.uProps[rowProp];
    // столбцы - общие параметры
    for (var colModel in DATA.cProps) {
      var colProps = DATA.cProps[colModel];
      for (var colProp in colProps) {
        if (colProp === 'propsOrder') continue;
        // пользовательский параметр не может совпадать с общим
        // общие параметры уже все есть в corrMatrix
        corrMatrix[rowProp][colProp] = corrMatrix[colProp][rowProp];
      }
    }
    // столбцы - пользовательские параметры
    for (var colProp in DATA.uProps) {
      var colPropData = DATA.uProps[colProp];
      if (rowProp !== colProp) {
        if (colProp in corrMatrix) {
          corrMatrix[rowProp][colProp] = corrMatrix[colProp][rowProp];
        }
        else {
          corrMatrix[rowProp][colProp] = Correlation(rowPropData, colPropData);
        }
      }
    }
  }
  DATA.corrMatrix = corrMatrix;
  console.timeEnd('calcCorr');
}

function buildData() { //{{{1
  // Минимальная и максимальная даты (полагаемся на сортировку, произведённую на сервере)
  DATA.minDate = new Date(DATA.dates[DATA.dates.length-1]).valueOf();
  DATA.maxDate = new Date(DATA.dates[0]).valueOf();
  
  // Статистические показатели
  for (var model in DATA.cProps) {
    for (var prop in DATA.cProps[model]) {
      if (prop !== 'propsOrder') calcStat(DATA.cProps[model][prop]);
    }
  }
  for (var prop in DATA.uProps) {
    calcStat(DATA.uProps[prop]);
  }

  // Корреляционная матрица
  calcCorr();
}
//}}}
//function buildPropsTable(withDate, check, disableEmpty, withButtons) {{{1
// Создание таблицы с выбором параметров
function buildPropsTable(withDate, check, disableEmpty, withButtons) {
  if (typeof(withDate) == 'undefined') withDate = false;
  if (typeof(check) == 'undefined') check = {uProps:1};
  if (typeof(disableEmpty) == 'undefined') disableEmpty = false;
  if (typeof(withButtons) == 'undefined') withButtons = false;
  var html = '<table class="propsTable"><thead><tr>';
  if (withDate) {html += '<th>Дата</th>';}
  if ('cProps' in DATA) {html += '<th>'+_('Общие параметры')+'</th>';}
  if ('uProps' in DATA) {html += '<th>'+_('Пользовательские параметры')+'</th>';}
  html += '</tr></thead>';
  html += '<tbody><tr>';
  // Ячейка с датой
  if (withDate) {
    html += '<td><ul class="markerless"><li><label><input type="checkbox" name="date" value="date"/>'+_('Дата')+'</label></li></ul><ul style="font-size:80%;margin-top:10px;">'+_('Тип графика:')+'<li><label><input type="radio" name="chartType" value="scatter" checked/> '+_('точки')+'</label></li><li><label><input type="radio" name="chartType" value="line"/> '+_('линия')+'</label></li></ul></td>'
  }
  // Ячейка с общими параметрами
  if ('cProps' in DATA) {
    html += '<td><ul class="markerless">';
    for (var i=0; i<DATA.modelsOrder.length; i++) {
      var model = DATA.modelsOrder[i];
      html += '<p><b>' + modelMap[model] + '</b></p>';
      var props = DATA.cProps[model];
      for (var j=0; j<props.propsOrder.length; j++) {
        var prop = props.propsOrder[j];
        var propData = props[prop];
        var checked='', disabled='', noData='', class_='';
        if ('cProps' in check) {checked = ' checked';}
        if (disableEmpty && propData.stat.n===0) {
          checked = '';
          disabled = ' disabled';
          class_ = ' class="disabled"';
          noData = _(' (нет данных)');
        }
        html += '<li><label' + class_ + '><input type="checkbox"' + checked + disabled + ' name="cProps" value="' + prop + '"/>' + propData.repr + noData + '</label></li>';
      }
    }
    html += '</ul>';
    if (withButtons) {
      html += '<p><button name="selectAll" type="button">'+_('Отметить все')+'</button><button name="deselectAll" type="button">'+_('Снять отметку со всех')+'</button></p>';
    }
    html += '</td>';
  }
  // Ячейка с пользовательскими параметрами, если есть
  if ('uProps' in DATA) {
    html += '<td><ul class="markerless">';
    var uProps = DATA.uPropsOrder;
    for (var i=0; i<uProps.length; i++) {
      var prop = uProps[i];
      var propData = DATA.uProps[prop];
      var checked='', disabled='', noData='', class_='';
      if ('uProps' in check) {checked = ' checked';}
      if (disableEmpty && propData.stat.n===0) {
        checked = '';
        disabled = ' disabled';
        class_ = ' class="disabled"';
        noData = _(' (нет данных)');
      }
      html += '<li><label' + class_ + '><input type="checkbox"' + checked + disabled + ' name="uProps" value="' + prop + '"/>' + propData.repr + noData + '</label></li>';
    }
    html += '</ul>';
    if (withButtons) {
      html += '<p><button name="selectAll" type="button">'+_('Отметить все')+'</button><button name="deselectAll" type="button">'+_('Снять отметку со всех')+'</button></p>';
    }
    html += '</td>';
  }

  html += '</tr></tbody></table>';
  
  return html;
}

//function buildForms() {{{1
// Создание форм для выбора параметров и/или дат
function buildForms() {
  // Форма при графике
  var html = _('<form><p>В форме, представленной ниже, можно отметить параметры и построить по ним график.<br/>Отметить можно не более двух параметров.<br/>Если отмечен 1 параметр, то будет показана гистограмма распределения.<br/>Если отмечены 1 параметр и "Дата", то будет показан график динамики показателя.<br/>Если отмечены 2 параметра, то будет показан график рассеяния, где по оси X откладываются значения одного показателя, а по оси Y &mdash; другого.</p>');
  html += buildPropsTable(true, {}, true, false);
  html += '<input type="button" id="drawChart" value="'+_('Построить график')+'" /></form>';
  $I('props4charts').innerHTML = html;
  
  // Форма при таблице со статистическими показателями
  var html = _('<form><p>В форме можно выбрать параметры, данные по которым будут отображаться в таблице.</p>');
  if ('uProps' in DATA) {
    html += buildPropsTable(false, {uProps:1}, false, true);
  }
  else {
    html += buildPropsTable(false, {cProps:1}, false, true);
  }
  html += '<input type="button" id="rebuildStattable" value="'+_('Обновить таблицу')+'" /></form>';
  $I('props4statTable').innerHTML = html;

  // Форма при корреляционной таблице
  var html = _('<form><p>В форме можно выбрать параметры, данные по которым будут отображаться в таблице.</p>');
  html += buildPropsTable(false, {cProps:1, uProps:1}, false, true);
  html += '<input type="button" id="rebuildCorrtable" value="'+_('Обновить таблицу')+'"/></form>';
  $I('props4corrTable').innerHTML = html;

  // Форма при таблице с данными
  var html = _('<form><p>В форме можно выбрать параметры и даты, данные по которым будут отображаться в таблице.</p>');
  if ('uProps' in DATA) {
    html += buildPropsTable(false, {uProps:1}, false, true);
  }
  else {
    html += buildPropsTable(false, {cProps:1}, false, true);
  }
  var minDate = new Date(DATA.minDate).toISOString().split('T')[0];
  var maxDate = new Date(DATA.maxDate).toISOString().split('T')[0];
  html += '<p id="datesCaption"><b>'+_('Даты:')+'</b> <span class="error"></span></p><div id="dates"><p><label for="dateFrom4dataTable">'+_('С')+' </label><input id="dateFrom4dataTable" type="date" name="dateFrom4dataTable" value="' + minDate + '" min="' + minDate + '" max="' + maxDate + '"/><label for="dateTo4dataTable"> '+_('по')+' </label><input id="dateTo4dataTable" type="date" name="dateTo4dataTable" value="' + maxDate + '" min="' + minDate + '" max="' + maxDate + '"/></p></div><input type="button" id="rebuildDatatable" value="'+_('Обновить таблицу')+'" /></form>';
  $I('props4dataTable').innerHTML = html;

  finalizeForms();
}

//function finalizeForms() {{{1
// Окончательное оформление форм
function finalizeForms() {
  // Кнопки "Отметить все" {{{2
  var saButtons = document.getElementsByName('selectAll');
  for (var i=0; i<saButtons.length; i++) {
    saButtons[i].onclick = function() {
      var cbs = this.parentNode.previousSibling.querySelectorAll('input[type="checkbox"]');
      for (var j=0,l=cbs.length; j<l; j++) {
        cbs[j].checked = true;
      }
    }
  }
  // Кнопки "Снять отметку со всех" {{{2
  var daButtons = document.getElementsByName('deselectAll');
  for (var i=0; i<saButtons.length; i++) {
    daButtons[i].onclick = function() {
      var cbs = this.parentNode.previousSibling.querySelectorAll('input[type="checkbox"]');
      for (var j=0,l=cbs.length; j<l; j++) {
        cbs[j].checked = false;
      }
    }
  }
  // Поля выбора дат {{{2
  if (navigator.userAgent.toLowerCase().indexOf('firefox') !== -1) {
    var selectors = false; //не работает выбор в firefox>=20(17esr) (https://github.com/jquerytools/jquerytools/issues/982)
  }
  else {
    var selectors = true;
  };
  var dateInputs = [$I('dateFrom4dataTable'), $I('dateTo4dataTable')];
  // Если дата не в формате ISO, преобразовываем в iso-формат (иначе dateinput oставит текущую дату)
  if (lang === 'en') {
    var format = 'dd/mm/yyyy';
  }
  else {
    var format = 'dd.mm.yyyy';
  }
  for (var i=0; i<dateInputs.length; i++) {
    var I = dateInputs[i];
    I.value = I.value.replace(ruFormat, "$3-$2-$1").replace(enFormat, "$3-$2-$1");
    $(I).dateinput({lang:lang, format:format, selectors:selectors, firstDay:1});
  }
  // Не более 2 чекбоксов в форме для графиков {{{2
  var cbs = $QA('#props4charts input[type=checkbox]');
  for (var i=0; i<cbs.length; i++) {
    cbs[i].onchange = function() {
      if (this.checked) {
        chartCbsChecked.push(this);
        if (chartCbsChecked.length > 2) {
          chartCbsChecked.shift().checked = false;
        }
      }
      else {
        var j = chartCbsChecked.indexOf(this);
        if (j !== -1) { chartCbsChecked.splice(j,1); }
      }
    }
  }
  // Кнопки "Обновить таблицу" {{{2
  $I('rebuildDatatable').onclick = buildDatatable;
  $I('rebuildStattable').onclick = buildStattable;
  $I('rebuildCorrtable').onclick = buildCorrtable;
  $I('drawChart').onclick = buildChart;
}

//function buildHeader(aProps, withMeasure) {{{1
function buildHeader(aProps, withMeasure) {
  withMeasure = withMeasure || false;
  
  var cProps = [];
  var uProps = [];
  var cPropsHeader = [];
  var uPropsHeader = [];
  var lastModel = undefined;
  var lastPlanet = undefined;
  var order = 2; // для атрибута data-csvorder в таблицах
  var types = [], i_type = 2; // для атрибута data-type в таблицах
  for (var i=0; i<aProps.length; i++) {
    var name = aProps[i].name;
    if (name === 'cProps') {
      var propname = aProps[i].value;
      var model = propname.split('.')[0];
      var propData = DATA.cProps[model][propname];
      var content = propData.repr;
      if (withMeasure === true && propData.measure && propData.measure !== '') {
        content += ', ' + propData.measure;
      }
      propData.name = propname; // for corrTable
      cProps.push(propData);
      types[i_type++] = propData.type;
      
      // параметры, принадлежащие одной модели, следуют по порядку
      if (model === lastModel) {
        if (model === 'AstroData') {
          var planet = propname.split('.')[1].split('_')[0];
          if (planet === lastPlanet) {
            var aPlanets = cPropsHeader[cPropsHeader.length-1][2];
            var content = content.substr(content.indexOf(',')+2);
            cPropsHeader[cPropsHeader.length-1][1]++;
            aPlanets[aPlanets.length-1][1]++;
            var P = {content:content, order:order++};
            aPlanets[aPlanets.length-1][2].push(P);
          }
          else {
            var planetName = content.split(',')[0];
            var content = content.substr(content.indexOf(',')+2);
            cPropsHeader[cPropsHeader.length-1][1]++;
            var P = {content:content, order:order++};
            cPropsHeader[cPropsHeader.length-1][2].push([planetName, 1, [P]]);
          }
          lastPlanet = planet;
        }
        else {
          cPropsHeader[cPropsHeader.length-1][1]++;
          var P = {content:content, order:order++};
          cPropsHeader[cPropsHeader.length-1][2].push(P);
        }
      }
      else {
        if (model === 'AstroData') {
          var planet = propname.split('.')[1].split('_')[0];
          var planetName = content.split(',')[0];
          var content = content.substr(content.indexOf(',')+2);
          var P = {content:content, order:order++};
          cPropsHeader.push([modelMap[model], 1, [[planetName, 1, [P]]]]);
          lastPlanet = planet;
        }
        else {
          var P = {content:content, order:order++};
          cPropsHeader.push([modelMap[model], 1, [P]]);
        }
        lastModel = model;
      };
    }
    else if (name === 'uProps') {
      var id = aProps[i].value;
      var propData = DATA.uProps[id];
      var content = propData.repr;
      if (withMeasure === true && propData.measure && propData.measure !== '') {
        content += ', ' + propData.measure;
      };
      propData.id = id; // for corrTable
      uProps.push(propData);
      types[i_type++] = propData.type;
      var P = {content:content, order:order++};
      uPropsHeader.push(P);
    };
  };

  return {
    cProps: cProps,
    uProps: uProps,
    cPropsHeader: cPropsHeader,
    uPropsHeader: uPropsHeader,
    types: types
  };
}

function buildDatatable() { //{{{1
  console.time('dataTable');
  var container = $I('datatableContainer');
  var empty = '&nbsp;';

  // формируем списки показателей и заголовки
  var aProps = $QA('#props4dataTable input[name$="Props"]:checked');
  var result = buildHeader(aProps, true);
  var cProps = result.cProps;
  var uProps = result.uProps;
  var cPropsHeader = result.cPropsHeader;
  var uPropsHeader = result.uPropsHeader;
  var types = result.types;

  // Даты
  var dateFrom = new Date($I('dateFrom4dataTable').value.replace(ruFormat, '$3-$2-$1').replace(enFormat, "$3-$2-$1"));
  var dateTo = new Date($I('dateTo4dataTable').value.replace(ruFormat, '$3-$2-$1').replace(enFormat, "$3-$2-$1"));
  if (dateFrom > dateTo) {
    $Q('#datesCaption span.error').innerHTML = _('ОШИБКА! Дата "с" не может быть позднее даты "по".');
    return false;
  }
  else {
    $Q('#datesCaption span.error').innerHTML = '';
  };

  var cols = 1; // для строки с номерами столбцов
  var cpl = cProps.length;
  var upl = uProps.length;

  // Пэйджер
  var pagerHtml = '<div class="pager">' +
   '<img src="/img/first.png" class="first" title="'+_('Первая страница')+'"/>' +
   '<img src="/img/prev.png" class="prev" title="'+_('Предыдущая страница')+'"/>' +
   '<span class="pagedisplay"></span>' +
   '<img src="/img/next.png" class="next" title="'+_('Следующая страница')+'"/>' +
   '<img src="/img/last.png" class="last" title="'+_('Последняя страница')+'"/>' +
   '<select class="pagesize" title="'+_('Количество строк на странице')+'">' +
    '<option value="10">10</option>' +
    '<option selected="selected" value="20">20</option>' +
    '<option value="30">30</option>' +
    '<option value="40">40</option>' +
    '<option value="50">50</option>' +
   '</select>' +
   '<select class="gotoPage" title="'+_('Выберите номер страницы')+'"></select>' +
  '</div>';
  // пэйджер сверху
  var html = pagerHtml;

  // Собираем таблицу
  html += '<table id="dataTable" class="tablesorter">';
  // Заголовок (5 строк)
  html += '<thead>';

  // первая строка: "Дата", "Общие параметры", "Пользовательские параметры"
  html += '<tr class="header">';
  // атрибут data-csvheader используется при создании csv
  html += '<td rowspan="4" data-csvheader="Дата" data-csvorder="1">'+_('Дата')+'</td>';
  // общие параметры
  if (cpl !== 0) {
    var colspan = cpl;
    html += '<td colspan="' + colspan + '">'+_('Общие параметры')+'</td>';
    cols += colspan;
  };
  // пользовательские параметры
  if (upl !== 0) {
    var colspan = upl;
    html += '<td colspan="' + colspan + '">'+_('Пользовательские параметры')+'</td>';
    cols += colspan;
  };
  html += '</tr>';

  // вторая строка: названия групп общих параметров и названия пользовательских параметров
  html += '<tr class="header">';
  // общие параметры
  for (var i=0; i<cPropsHeader.length; i++) {
    var text = cPropsHeader[i][0];
    var colspan = cPropsHeader[i][1];
    html += '<td colspan="' + colspan + '">' + text + '</td>';
  };
  // пользовательские параметры
  for (var i=0; i<uPropsHeader.length; i++) {
    var P = uPropsHeader[i];
    html += '<td rowspan="3" data-csvheader="'+P.content+'" data-csvorder="'+P.order+'">'+P.content+'</td>';
  }
  html += '</tr>';

  // третья строка: названия общих параметров и планет
  html += '<tr class="header">'
  for (var i=0; i<cPropsHeader.length; i++) {
    var props = cPropsHeader[i][2];
    for (var j=0; j<props.length; j++) {
      var P = props[j];
      if (P instanceof Array) {
        var text = P[0];
        var colspan = P[1];
        html += '<td colspan="' + colspan + '">' + text + '</td>';
      }
      else {
        html += '<td rowspan="2" data-csvheader="'+P.content+'" data-csvorder="'+P.order+'">'+P.content+'</td>';
      }
    }
  };
  html += '</tr>';

  // четвёртая строка: показатели планет
  html += '<tr class="header">';
  for (var i=0; i<cPropsHeader.length; i++) {
    var props = cPropsHeader[i][2];
    for (var j=0; j<props.length; j++) {
      var prop = props[j];
      if (prop instanceof Array) {
        var ephes = prop[2];
        for (var k=0; k<ephes.length; k++) {
          var P = ephes[k];
          var csvHeader = prop[0] + ', ' + P.content;
          html += '<td data-csvheader="'+csvHeader+'" data-csvorder="'+P.order+'">'+P.content+'</td>';
        }
      }
    }
  }
  html += '</tr>';

  // пятая строка: номера столбцов (единственная с th)
  html += '<tr class="colnumbers">';
  for (var i=1; i<=cols; i++) {
    var dataType = '';
    if (i === 1) {dataType = ' data-type="date"';}
    else {
      if (types[i]) {dataType = ' data-type="' + types[i] + '"';}
    }
    html += '<th'+dataType+'>' + i + '</th>';
  };
  html += '</tr>';
  html += '</thead>';

  // Тело таблицы
  html += '<tbody>';
  var dates = DATA.dates;
  // Заполняем данные
  for (var i=0; i<dates.length; i++) {
    var date = new Date(dates[i]);
    if (date >= dateFrom && date <= dateTo) {
      html += '<tr>';
      html += '<td>' + formatDate(date) + '</td>';
      // общие параметры
      for (var j=0; j<cProps.length; j++) {
        var value = cProps[j].trend[i];
        var type = cProps[j].type;
        var maps = cProps[j].maps; // для type==='circ_cat' (с.в. undefined)
        if (value === null) {
          var content = empty;
        }
        else {
          var content = format(value, type, maps);
        };
        html += '<td>' + content + '</td>';
      };
      // пользовательские параметры
      for (var j=0; j<uProps.length; j++) {
        var propData = uProps[j];
        var value = propData.trend[i];
        var type = propData.type;
        if (value === null) {
          var content = empty;
        }
        else {
          var content = format(value, type);
        };
        html += '<td>' + content + '</td>';
      };
      html += '</tr>';
    };
  };
  html += '</tbody>';

  html += '</table>';

  // Пэйджер снизу
  html += pagerHtml;

  container.innerHTML = html; // вставка
  datatableSort(); // сортировка
  console.timeEnd('dataTable');
}

//}}}
//function buildStattable() {{{1
function buildStattable() {
  console.time('statTable');
  var container = $I('stattableContainer');
  var empty = '--';

  // формируем списки показателей и заголовки
  var aProps = $QA('#props4statTable input[name$="Props"]:checked');
  var result = buildHeader(aProps, true);
  var cProps = result.cProps;
  var uProps = result.uProps;
  var cPropsHeader = result.cPropsHeader;
  var uPropsHeader = result.uPropsHeader;
  var types = result.types;

  var cols = 1; // для строки с номерами столбцов
  var cpl = cProps.length;
  var upl = uProps.length;

  // Собираем таблицу
  var html = '<table id="statTable">';
  // Заголовок (5 строки)
  html += '<thead>';

  // первая строка: "Показатель", "Общие параметры",  "Пользовательские параметры"
  html += '<tr>';
  html += '<th rowspan="4" data-csvheader="Показатель" data-csvorder="1">'+_('Показатель')+'</th>';
  // общие параметры
  if (cpl !== 0) {
    var colspan = cpl;
    html += '<th colspan="' + colspan + '">'+_('Общие параметры')+'</th>';
    cols += colspan;
  };
  // пользовательские параметры
  if (upl !== 0) {
    var colspan = upl;
    html += '<th colspan="' + colspan + '">'+_('Пользовательские параметры')+'</th>';
    cols += colspan;
  };
  html += '</tr>';

  // вторая строка: названия групп общих параметров и названия пользовательских параметров
  html += '<tr>';
  // общие параметры
  for (var i=0; i<cPropsHeader.length; i++) {
    var text = cPropsHeader[i][0];
    var colspan = cPropsHeader[i][1];
    html += '<th colspan="' + colspan + '">' + text + '</th>';
  };
  // пользовательские параметры
  for (var i=0; i<uPropsHeader.length; i++) {
    var P = uPropsHeader[i];
    html += '<th rowspan="3" data-csvheader="'+P.content+'" data-csvorder="'+P.order+'">'+P.content+'</th>';
  }
  html += '</tr>';

  // третья строка: названия общих параметров и планет
  html += '<tr class="header">'
  for (var i=0; i<cPropsHeader.length; i++) {
    var props = cPropsHeader[i][2];
    for (var j=0; j<props.length; j++) {
      var P = props[j];
      if (P instanceof Array) {
        var text = P[0];
        var colspan = P[1];
        html += '<th colspan="' + colspan + '">' + text + '</th>';
      }
      else {
        html += '<th rowspan="2" data-csvheader="'+P.content+'" data-csvorder="'+P.order+'">'+P.content+'</th>';
      }
    }
  };
  html += '</tr>';

  // четвёртая строка: показатели планет
  html += '<tr class="header">';
  for (var i=0; i<cPropsHeader.length; i++) {
    var props = cPropsHeader[i][2];
    for (var j=0; j<props.length; j++) {
      var prop = props[j];
      if (prop instanceof Array) {
        var ephes = prop[2];
        for (var k=0; k<ephes.length; k++) {
          var P = ephes[k];
          var csvHeader = prop[0] + ', ' + P.content;
          html += '<th data-csvheader="'+csvHeader+'" data-csvorder="'+P.order+'">'+P.content+'</th>';
        }
      }
    }
  }
  html += '</tr>';

  // пятая строка: номера столбцов
  html += '<tr class="colnumbers">';
  for (var i=1; i<=cols; i++) {
    var dataType = '';
    if (i === 1) {dataType = ' data-type="name"'}
    else {
      if (types[i]) {dataType = ' data-type="' + types[i] + '"';}
    }
    html += '<th'+dataType+'>' + i + '</th>';
  };
  html += '</tr>';
  html += '</thead>';

  // Тело таблицы
  html += '<tbody>';
  var statistics = [
    ['n', _('Количество значений')],
    ['min', _('Минимальное значение')],
    ['max', _('Максимальное значение')],
    ['mean', _('Среднее значение')],
    ['stdev', _('Стандартное отклонение')]
  ];
  for (var i=0; i<statistics.length; i++) {
    var statName = statistics[i][0];
    var statRepr = statistics[i][1];
    html += '<tr>';
    html += '<th>'+statRepr+'</th>';
    // общие параметры
    for (var j=0; j<cProps.length; j++) {
      var value = cProps[j].stat[statName];
      var type = cProps[j].type;
      var maps = cProps[j].maps; // для type==='circ_cat' (с.в. undefined)
      var content = formatStat(value, statName, type, maps);
      if (content === null) {
        var content = empty;
      };
      html += '<td>'+content+'</td>';
    };
    // пользовательские параметры
    for (var j=0; j<uProps.length; j++) {
      var value = uProps[j].stat[statName]
      var type = uProps[j].type;
      var content = formatStat(value, statName, type);
      if (content === null) {
        var content = empty;
      };
      html += '<td>'+content+'</td>';
    };
    html += '</tr>';
  };
  html += '</tbody>';

  html += '</table>';

  container.innerHTML = html; // вставка
  console.timeEnd('statTable');
}

//function buildCorrtable() {{{1
function buildCorrtable() {
  console.time('corrTable');
  var container = $I('corrtableContainer');
  var empty = '--';
  
  // формируем списки показателей и заголовки
  var aProps = $QA('#props4corrTable input[name$="Props"]:checked');
  var result = buildHeader(aProps, false);
  var cProps = result.cProps;
  var uProps = result.uProps;
  var cPropsHeader = result.cPropsHeader;
  var uPropsHeader = result.uPropsHeader;

  var cols = 1; // для строки с номерами столбцов
  var cpl = cProps.length;
  var upl = uProps.length;

  // Собираем таблицу
  var html = '<table id="corrTable">';
  // Заголовок (5 строк)
  html += '<thead>';

  // первая строка: пустая ячейка, "Общие параметры", "Пользовательские параметры"
  html += '<tr>';
  html += '<th rowspan="4" data-csvheader="" data-csvorder="1">&nbsp;</th>';
  // общие параметры
  if (cpl !== 0) {
    var colspan = cpl;
    html += '<th colspan="' + colspan + '">'+_('Общие параметры')+'</th>';
    cols += colspan;
  };
  // пользовательские параметры
  if (upl !== 0) {
    var colspan = upl;
    html += '<th colspan="' + colspan + '">'+_('Пользовательские параметры')+'</th>';
    cols += colspan;
  };
  html += '</tr>';

  // вторая строка: названия групп общих параметров и названия пользовательских параметров
  html += '<tr>';
  // общие параметры
  for (var i=0; i<cPropsHeader.length; i++) {
    var text = cPropsHeader[i][0];
    var colspan = cPropsHeader[i][1];
    html += '<th colspan="' + colspan + '">' + text + '</th>';
  };
  // пользовательские параметры
  for (var i=0; i<uPropsHeader.length; i++) {
    var P = uPropsHeader[i];
    html += '<th rowspan="3" data-csvheader="'+P.content+'" data-csvorder="'+P.order+'">'+P.content+'</th>';
  }
  html += '</tr>';

  // третья строка: названия общих параметров и планет
  html += '<tr class="header">'
  for (var i=0; i<cPropsHeader.length; i++) {
    var props = cPropsHeader[i][2];
    for (var j=0; j<props.length; j++) {
      var P = props[j];
      if (P instanceof Array) {
        var text = P[0];
        var colspan = P[1];
        html += '<th colspan="' + colspan + '">' + text + '</th>';
      }
      else {
        html += '<th rowspan="2" data-csvheader="'+P.content+'" data-csvorder="'+P.order+'">'+P.content+'</th>';
      }
    }
  };
  html += '</tr>';

  // четвёртая строка: показатели планет
  html += '<tr class="header">';
  for (var i=0; i<cPropsHeader.length; i++) {
    var props = cPropsHeader[i][2];
    for (var j=0; j<props.length; j++) {
      var prop = props[j];
      if (prop instanceof Array) {
        var ephes = prop[2];
        for (var k=0; k<ephes.length; k++) {
          var P = ephes[k];
          var csvHeader = prop[0] + ', ' + P.content;
          html += '<th data-csvheader="'+csvHeader+'" data-csvorder="'+P.order+'">'+P.content+'</th>';
        }
      }
    }
  }
  html += '</tr>';

  // пятая строка: номера столбцов
  html += '<tr class="colnumbers">';
  for (var i=1; i<=cols; i++) {
    var dataType = '';
    if (i === 1) {dataType = ' data-type="name"';}
    else {dataType = ' data-type="float2"';}
    html += '<th'+dataType+'>' + i + '</th>';
  };
  html += '</tr>';
  html += '</thead>';

  // Тело таблицы
  html += '<tbody>';
  // в рядах общие параметры
  for (var i=0; i<cProps.length; i++) {
    var prop1 = cProps[i].name;
    html += '<tr>';
    html += '<th>' + cProps[i].repr + '</th>';
    for (var j=0; j<cProps.length; j++) {
      var prop2 = cProps[j].name;
      if (prop1 === prop2) {
        html += '<td class="diagonal">&nbsp;</td>';
      }
      else {
        html += formatCorrTd(DATA.corrMatrix[prop1][prop2]);
      };
    };
    for (var j=0; j<uProps.length; j++) {
      var prop2 = uProps[j].id;
      html += formatCorrTd(DATA.corrMatrix[prop1][prop2]);
    };
    html += '</tr>';
  };
  // в рядах пользовательские параметры
  for (var i=0; i<uProps.length; i++) {
    var prop1 = uProps[i].id;
    html += '<tr>';
    html += '<th>' + uProps[i].repr + '</th>';
    for (var j=0; j<cProps.length; j++) {
      var prop2 = cProps[j].name;
      html += formatCorrTd(DATA.corrMatrix[prop1][prop2]);
    };
    for (var j=0; j<uProps.length; j++) {
      var prop2 = uProps[j].id;
      if (prop1 === prop2) {
        html += '<td class="diagonal">&nbsp;</td>';
      }
      else {
        html += formatCorrTd(DATA.corrMatrix[prop1][prop2]);
      };
    };
    html += '</tr>';
  }
  html += '</tbody>';

  html += '</table>';

  container.innerHTML = html;
  console.timeEnd('corrTable');
}

// function buildChart() {{{1
function buildChart() {
  //Подготовка {{{2
  console.time('chart');
  var container = $('#chartContainer');
  if (container.highcharts() !== undefined) {
    container.highcharts().destroy();
  }
  // Зануление графика
  var Chart = {};

  var cbsLen = chartCbsChecked.length;
  if (cbsLen < 1) {
    container.html('<p class="error">'+_('Вы не выбрали ни одного параметра для построения графика!')+'</p>');
    return false;
  }
  var pNames = [];
  for (var i=0; i<cbsLen; i++) {
    pNames.push(chartCbsChecked[i].value);
  }
  
  // 1 показатель (гистограмма распределения) {{{2
  if (cbsLen === 1) {
    // Подготовка {{{3
    var pName = pNames[0];
    if (pName === 'date') {
      container.html('<p class="error">'+_('Гистограмму распределения можно построить только по параметрам, но не по дате!')+'</p>');
      return false;
    };
    var P;
    if (pName in DATA.uProps) {
      P = DATA.uProps[pName];
    }
    else {
      var model = pName.split('.')[0];
      P = DATA.cProps[model][pName];
    }
    var bars = GetBars(P);

    // Столбцы по интервалам {{{3
    if ('points' in bars) {
      // Объект графика
      Chart = {
        chart: {
          type: 'column'
        },
        title: {
          text: P.repr
        },
        legend: {
          enabled: false
        },
        xAxis: {
          min: 0,
          max: bars.data.length,
          tickInterval: 1,
          labels: {
            formatter: function() { return bars.points[this.value]; }
          }
        },
        yAxis: {
          title: {
            text: _('Количество значений')
          }
        },
        tooltip: {
          formatter: function() {
            var X = bars.points[this.x-0.5];
            var Y = bars.points[this.x+0.5];
            var beginBrace = this.x===0.5 ? '[' : '(';
            var interval = beginBrace + X + ', ' + Y + ']';
            return _('Интервал: <b>') + interval + '</b><br/>' + _('Количество: <b>') + this.y + '</b>';
          }
        },
        plotOptions: {
          column: {
            groupPadding: 0,
            pointPadding: 0,
            borderWidth: 0
          }
        },
        series: [{
          name: _('Количество'),
          data: bars.data,
          dataLabels: {
            enabled: true
          }
        }]
      };

    } // if ('points' in bars)
    
    // Столбцы по категориям {{{3
    else {
      var categories = [];
      var barsData = [];
      for (bar in bars) {
        categories.push(bar);
        barsData.push(bars[bar]);
      }
      
      // График в полярной системе координат {{{4
      if (P.type==='circ' || P.type==='circ_cat' || P.type==='time') {
        if (P.type === 'circ_cat') {
          var pointPlacement = 'on';
        }
        else {
          var pointPlacement = 'between';
        }
        if (P.type === 'circ_cat') {
          var tickmarkPlacement = 'between';
        }
        else {
          var tickmarkPlacement = 'on';
        }

        Chart = {
          chart: {
            type: 'column',
            polar: true,
            width: 960,
            height: 960
          },
          title: {
            text: P.repr
          },
          legend: {
            enabled: false
          },
          xAxis: {
            categories: categories,
            tickmarkPlacement: tickmarkPlacement
          },
          yAxis: {
            maxPadding: 0.02,
            title: {
              text: _('Частота'),
              rotation: 270,
              style: {color:'#db6200'}
            },
            labels: {
              style: {color:'#000'},
              formatter: function() { return this.value + '%'; }
            }
          },
          tooltip: {
            formatter: function() {
              if (P.type === 'circ_cat') {
                var X = P.maps.cat_tooltip[this.x];
              }
              else if (P.type === 'circ') {
                var Xnext = parseInt(this.x) + P.cat_step;
                var X = this.x + "° - " + Xnext + "°";
              }
              else if (P.type === 'time') {
                var X = this.x + " - " + (parseInt(this.x)+1);
              }
              return P.repr + ": <b>" + X + "</b><br/>" + this.series.name + ": <b>" + this.y + " %</b>"; 
            }
          },
          plotOptions: {
            column: {
              groupPadding: 0,
              pointPadding: 0,
              borderWidth: 1,
              pointPlacement: pointPlacement
            }
          },
          series: [{
            name: _('Частота'),
            data: barsData,
            dataLabels: {
              enabled: false
            }
          }]
        };
      } //if (P.type === 'time')
      // График в прямоугольной системе координат {{{4
      else {
        Chart = {
          chart: {
            type: 'column'
          },
          title: {
            text: P.repr
          },
          legend: {
            enabled: false
          },
          xAxis: {
            categories: categories
          },
          yAxis: {
            title: {
              text: _('Количество значений')
            }
          },
          tooltip: {
            formatter: function() {return _('Значение: <b>') + this.x + '</b><br/>' + _('Количество: <b>') + this.y + '</b>';}
          },
          series: [{
            name: _('Количество'),
            data: barsData,
            dataLabels: {
              enabled: true
            }
          }]
        };
      } //else (P.type === 'time')
    } // else ('points' in bars)
  } // if (cbsLen === 1)
  // 2 показателя {{{2
  else {
    // 1 показатель - дата (time series chart) {{{3
    if (pNames[0]==='date' || pNames[1]==='date') {
      // отображение дата:значение
      if (pNames[0] === 'date') {
        var pName = pNames[1];
      }
      else {
        var pName = pNames[0];
      }
      var P;
      if (DATA['uProps'] && pName in DATA.uProps) {
        P = DATA.uProps[pName];
      }
      else {
        var model = pName.split('.')[0];
        P = DATA.cProps[model][pName];
      }
      // Тип графика
      var chartType = $Q('input[name="chartType"]:checked').value;
      var trend = P.trend;
      var dates = DATA.dates;
      var dl = dates.length;
      var seriesData = []; 
      if (chartType === 'scatter') {
        for (var i=0; i<dl; i++) {
          seriesData.push([new Date(dates[i]).getTime(), format4line(trend[i], P)]);
        }
      }
      else { // chartType === 'line'
        // формируем ряд за ВСЕ даты с начальной по конечную. Если данных за дату нет, то null
        // при наличии пропусков len(seriesData) > len(dates)
        var dateStart = DATA.minDate;
        var datePrev = dateStart;
        var dateInterval = 86400000; // 1 сутки
        var pairs = [];
        for (var i=0; i<dl; i++) {
          pairs.push([new Date(dates[i]).getTime(), trend[i]]);
        }
        // в общем случае даты и данные не сортированы
        pairs.sort(function(a,b){return (a[0]-b[0]);});
        for (var i=0,pl=pairs.length; i<pl; i++) {
          if (i === 0) {
            seriesData.push(format4line(pairs[i][1], P));
          }
          else {
            var date = pairs[i][0];
            while (datePrev !== date) {
              datePrev += dateInterval;
              if (datePrev === date) {
                seriesData.push(format4line(pairs[i][1], P));
              }
              else {
                seriesData.push(null);
              }
            }
          }
        }
      }
      // Заголовок графика
      var titleText = P.repr;
      if (P.measure) titleText += ', ' + P.measure;
      // Ряд с данными
      var series = [{
        name: P.repr,
        data: seriesData,
        marker: {
          radius: 3,
          fillColor: 'transparent',
          lineWidth: 1,
          lineColor: 'blue'
        }
      }];
      if (chartType === 'line') {
        series[0].marker.radius = 1;
        series[0].lineWidth = 2;
        series[0].pointStart = dateStart;
        series[0].pointInterval = dateInterval;
      }
      // Объект графика
      Chart = {
        chart: {
          type: chartType
        },
        title: {
          text: titleText
        },
        tooltip: {
          formatter: function() {
            var X = formatDate(new Date(this.x));
            var Y;
            if (P.type === 'duration') {
              var HHMM = hhmm(this.y);
              Y = HHMM[0] + _('ч ') + HHMM[1] + _('мин');
            }
            else {
              Y = this.y;
              if (P.measure) {Y += " " + P.measure};
            }
            return "<b>" + this.series.name + "</b><br/>" + X + ": <b>" + Y + '</b>'
          },
          crosshairs: true
        },
        legend: {
          enabled: false
        },
        xAxis: {
          title: {
            text: _('Дата')
          },
          labels: {
            formatter: function() {return formatDate(new Date(this.value));}
          },
          gridLineWidth: 1,
          gridLineColor: "#E0E0E0",
          gridLineDashStyle: "dash"
        },
        yAxis: {
          title: {
            text: null
          },
          maxPadding: 0.05,
          endOnTick: false,
          startOnTick: false
        },
        series: series
      }
      
      // Модификация графика под различные типы данных
      if (P.type==='circ_cat' || P.type==='time' || P.type==='bool') {
        Chart.tooltip.formatter = function() {
          var X = formatDate(new Date(this.x));
          if (P.type === 'circ_cat') {
            var Y = P.maps.cat_tooltip[P.maps.categories[this.y]];
          }
          else if (P.type === 'time') {
            var HHMM = hhmm(this.y)
            var Y = HHMM[0] + ":" + HHMM[1];
          }
          else { // P.type = 'bool'
            var Y = this.y===0 ? _('Ложь') : _('Истина');
          };
          return "<b>" + this.series.name + "</b><br/>" + X + ": <b>" + Y + '</b>'
        };
      }
      if (P.type === 'circ') {
        Chart.yAxis.min = 0;
        Chart.yAxis.max = 360;
        Chart.yAxis.tickInterval = 30;
        Chart.yAxis.startOnTick = true;
        Chart.yAxis.endOnTick = true;
      }
      if (P.type === 'time') {
        Chart.yAxis.min = 0;
        Chart.yAxis.max = 24;
        Chart.yAxis.tickInterval = 1;
        Chart.yAxis.startOnTick = true;
        Chart.yAxis.endOnTick = true;
      }
      if (P.type === 'circ_cat') {
        Chart.yAxis.categories = P.maps.categories;
      }
      if (P.type === 'bool') {
        Chart.yAxis.categories = [_('Ложь'), _('Истина')];
      }
      if (P.type==='circ_cat' || P.type==='bool') {
        Chart.yAxis.tickmarkPlacement = 'on';
        // min и max нужны для того, чтобы отображались все категории, в том числе и пустые
        Chart.yAxis.min = 0;
        Chart.yAxis.max = Chart.yAxis.categories.length - 1;
      };
    } // if (pNames[0]==='date' || pNames[1]==='date')
    
    // 2 показателя (scatter plot) {{{3
    else { // if (pNames[0]==='date' || pNames[1]==='date')
      // Данные для графика (Ps) {{{4
      var chartData = []; // список точек - объектов {name:дата, value1, value2} на каждую дату
      var Ps = [];
      for (var i=0; i<pNames.length; i++) {
        var pName = pNames[i];
        if (pName in DATA.uProps) {
          Ps.push(DATA.uProps[pName]);
        }
        else {
          var model = pName.split('.')[0];
          Ps.push(DATA.cProps[model][pName]);
        }
      }

      // определение вида графика (chartType) {{{4
      var chartType = 'rect';
      if (circTypes[Ps[0].type] || circTypes[Ps[1].type]) {
        if (circTypes[Ps[0].type] && circTypes[Ps[1].type]) {
          chartType = 'torus';
        }
        else {
          chartType = 'cylinder';
          // по оси X (первый) должен располагаться циркулярный параметр
          if (!circTypes[Ps[0].type]) { // not in
            Ps.reverse();// меняем параметры местами
          }
        }
      }

      // Формируем список точек в графике рассеяния (chartData) {{{4
      var X = []; // В этих массивах находятся значения параметров
      var Y = []; // (нужны для вычисления параметров регрессии)
      for (var i=0,l=DATA.dates.length; i<l; i++) {
        var D = formatDate(new Date(DATA.dates[i]));
        var x,y;
        for (var j=0; j<Ps.length; j++) {
          var P = Ps[j];
          var value = format4line(P.trend[i], P)
          if (j === 0) { x = value; }
          else { y = value; };
        }
        // отбрасываем null-ы
        if (x !== null && y !== null) {
          chartData.push( {name:D, x:x, y:y} );
          // r
          X.push(x);
          Y.push(y);
        }
      }

      // Данные графика рассеяния (series) {{{4
      var series = [{
        type: 'scatter',
        name: Ps[0].repr + " vs " + Ps[1].repr,
        showInLegend: false,
        data: chartData,
        pointPlacement: 'on',
        turboThreshold: 0,
        marker: {
          radius: 3,
          fillColor: 'transparent',
          lineWidth: 1,
          lineColor: 'blue'
        }
      }];

      // коэффициент корреляции (подзаголовок графика) {{{4
      var corr = DATA.corrMatrix[pNames[0]][pNames[1]];
      var r = corr.value;
      var rType = corr.type;
      var rMsgMap = {
        Pearson: _('Коэффициент корреляции Пирсона r = '),
        Spearman: _('Коэффициент ранговой корреляции Спирмена r = '),
        CircCirc: _('Коэффициент круговой корреляции r = '),
        BoolBool: _('Коэффициент контингенции ϕ = '),
        LinCirc: _('Коэффициент линейно-круговой корреляции r = '),
        LinCircRank: _('Коэффициент линейно-круговой ранговой корреляции r = '),
        noData: _('Для подсчёта коэффициента корреляции недостаточно данных')
      };
      var rMsg = rMsgMap[rType];

      // Круг в центра кругового графика (он первый) {{{4
      if (chartType==='cylinder' || chartType==='torus') {
        if (chartType === 'cylinder') {
          var seriesData = [Ps[1].stat.min];
        }
        else {
          var seriesData = [0];
        }
        series.unshift({
          name: 'center_circle',
          type: 'column',
          data: seriesData,
          xAxis: 1,
          showInLegend: false,
          enableMouseTracking: false,
          groupPadding: 0,
          pointPadding: 0,
          borderWidth: 0
        });
      }
      // Параметры уравнения регрессии {{{4
      else if (chartType === 'rect') {
        if (X.length >= 10) {
          try {
            var regrData = Regression(X,Y);
            // Данные тренда
            var regrLine = regrData.regrLine;
            var regrLineConfBottom = regrData.regrLineConfBottom;
            var regrLineConfTop = regrData.regrLineConfTop;
            var valuesConfBottom = regrData.valuesConfBottom;
            var valuesConfTop = regrData.valuesConfTop;
          }
          catch(err) {
            if (err === 'arrays not equal') {
              r = _('Ошибка! У массивов не совпадает размер.');
            }
            else if (err === 'not enough data') {
              ; // условие отработано в секции else
            }
          }
        }
        else {
          r = _('Недостаточно данных (< 10) для подсчёта коэффициента корреляции и линии регрессии');
        }
        // Данные графика тренда и доверительных кривых
        if (regrLine) {
          // тренд
          var regrSeries = {
            type: 'line',
            color: '#000000',
            name: _('Тренд'),
            marker: {
              enabled: false
            },
            enableMouseTracking: false,
            events: {
              legendItemClick: function() {
                // скрыть/показать линию регрессии вместе с доверительными кривыми
                if (this.visible) {
                  this.chart.series[2].hide();
                  this.chart.series[3].hide();
                  this.chart.series[4].hide();
                  this.chart.series[5].hide();
                }
                else {
                  this.chart.series[2].show();
                  this.chart.series[3].show();
                  this.chart.series[4].show();
                  this.chart.series[5].show();
                }
              }
            },
            data: regrLine
          };
          series.push(regrSeries);
          // нижняя граница линии регрессии
          var regrBottomSeries = {
            type: 'line',
            color: '#AA4643',
            dashStyle: 'Dash',
            lineWidth: 1,
            marker: {
              enabled: false
            },
            enableMouseTracking: false,
            showInLegend: false,
            data: regrLineConfBottom
          };
          series.push(regrBottomSeries);
          // верхняя граница линии регрессии
          var regrTopSeries = {
            type: 'line',
            color: '#AA4643',
            dashStyle: 'Dash',
            lineWidth: 1,
            marker: {
              enabled: false
            },
            enableMouseTracking: false,
            showInLegend: false,
            data: regrLineConfTop
          };
          series.push(regrTopSeries);
          // нижняя граница значений
          var valuesBottomSeries = {
            type: 'line',
            color: '#AA4643',
            lineWidth: 1,
            marker: {
              enabled: false
            },
            enableMouseTracking: false,
            showInLegend: false,
            data: valuesConfBottom
          };
          series.push(valuesBottomSeries);
          // верхняя граница значений
          var valuesTopSeries = {
            type: 'line',
            color: '#AA4643',
            lineWidth: 1,
            marker: {
              enabled: false
            },
            enableMouseTracking: false,
            showInLegend: false,
            data: valuesConfTop
          };
          series.push(valuesTopSeries);
        }
      }
      
      // if (chartType === 'cylinder') {{{4
      // первый параметр - циркулярный
      if (chartType === 'cylinder') {
        // xAxis
        var xAxis;
        if (Ps[0].type === 'circ_cat') {
          xAxis = [{
            categories: Ps[0].maps.categories,
            // min и max нужны для того, чтобы отображались все категории, в том числе и пустые
            min: 0,
            max: Ps[0].maps.categories.length
          }];
        }
        else if (Ps[0].type === 'time') {
          xAxis = [{min:0, max:24}];
        }
        else if (Ps[0].type === 'circ') {
          xAxis = [{min:0, max:360}];
        }
        // ось X для центрального круга
        xAxis.push({
          categories: ['one'],
          labels: {
            enabled: false
          }
        });

        // yAxis
        var yAxis;
        if (Ps[1].type === 'bool') {
          yAxis = {
            categories: [_('Ложь'), _('Истина')],
            min: -1,
            max: 1,
            showLastLabel: true,
            labels: {
              formatter: function() {
                if (this.value < 0) {return null;}
                else {return this.value;}
              },
              style: {color:'#db6200'}
            }
          };
        }
        else {
          var Ymin = Ps[1].stat.min;
          var Ymax = Ps[1].stat.max;
          var Yrange = Ymax - Ymin;
          Chart.yAxis = {
            maxPadding: 0.02,
            min: Ymin - Yrange/2,
            max: Ymax,
            labels: {
              formatter: function() {
                if (this.value > Ymin) {return this.value;}
              },
              style: {color:'#db6200'}
            }
          };
        }

        // Объект графика
        Chart = {
          chart: {
            width: 960,
            height: 960,
            polar: true
          },
          colors: ['#1f2933', '#0396b5'],
          pane: {
            background: {
              backgroundColor: {
                radialGradient: {cx:0.5, cy:0.5, r:0.5},
                stops: [
                  [0, '#000'],
                  [0.3, '#000'],
                  [0.65, '#777'],
                  [1, '#fff']
                ]
              },
              borderWidth: 0,
              outerRadius: '100%'
            }
          }, 
          title: {
            text: Ps[0].repr + " vs " + Ps[1].repr
          },
          subtitle: {
            text: typeof(r)==='number' ? rMsg + r.toFixed(2) : r
          },
          legend: {
            align: 'right',
            verticalAlign: 'middle'
          },
          xAxis: xAxis,
          yAxis: {}, // определяется позже
          tooltip: {
            formatter: function() {
              var X;
              if (Ps[0].type === 'circ') {
                X = this.x + " °";
              }
              else if (Ps[0].type === 'circ_cat') {
                X = Ps[0].maps.cat_tooltip[this.x];
              }
              else if (Ps[0].type === 'time') {
                var HHMM = hhmm(this.x);
                X = HHMM[0] + ":" + HHMM[1];
              }
              var Y;
              if (Ps[1].type === 'duration') {
                var HHMM = hhmm(this.y);
                Y = HHMM[0] + _('ч ') + HHMM[1] + _('мин');
              }
              else if (Ps[1].type === 'bool') {
                var Y = this.y===0 ? _('Ложь') : _('Истина');
              }
              else {
                Y = this.y;
                if (Ps[1].measure) {
                  Y += " " + Ps[1].measure;
                }
              }
              return "<b>" + this.point.name + "</b><br/>" + Ps[0].repr + ": <b>" + X + "</b><br/>" + Ps[1].repr + ": <b>" + Y + "</b>";
            }
          },
          series: series
        };
      } // if (chartType === 'cylinder')

      // else if (chartType === 'torus') {{{4
      else if (chartType === 'torus') {
        // xAxis
        var xAxis;
        if (Ps[0].type === 'circ_cat') {
          xAxis = [{
            categories: Ps[0].maps.categories,
            // min и max нужны для того, чтобы отображались все категории, в том числе и пустые
            min: 0,
            max: Ps[0].maps.categories.length
          }];
        }
        else if (Ps[0].type === 'time') {
          xAxis = [{min:0, max:24}];
        }
        else if (Ps[0].type === 'circ') {
          xAxis = [{min:0, max:360}];
        }
        // ось X для центрального круга
        xAxis.push({
          categories: ['one'],
          labels: {
            enabled: false
          }
        });

        // yAxis
        var yAxis;
        if (Ps[1].type === 'circ_cat') {
          yAxis = {
            categories: Ps[1].maps.categories,
            min: -1*Ps[1].maps.categories.length + 1,
            // max нужен, чтобы отображались все категории, в том числе и пустые
            max: Ps[1].maps.categories.length - 1,
            labels: {
              formatter: function() {
                if (this.value < 0) {return null;}
                else {return this.value;}
              },
              style: {color:'#db6200'},
            },
            tickmarkPlacement: 'on',
            showLastLabel: true
          };
        }
        else if (Ps[1].type === 'time') {
          yAxis = {
            min: -24,
            max: 24,
            tickInterval: 3,
            showLastLabel: true,
            labels: {
              formatter: function() {
                if (this.value < 0) {return null;}
                else {return this.value;}
              },
              style: {color:'#db6200'}
            }
          }
        }
        else if (Ps[1].type === 'circ') {
          yAxis = {
            min: -360,
            max: 360,
            tickInterval: 30,
            showLastLabel: true,
            labels: {
              formatter: function() {
                if (this.value < 0) {return null;}
                else {return this.value;}
              },
              style: {color:'#db6200'}
            }
          }
        }

        // Объект графика
        Chart = {
          chart: {
            width: 960,
            height: 960,
            polar: true
          },
          colors: ['#fff', '#0396b5'],
          pane: {
            background: {
              backgroundColor: {
                radialGradient: {cx:0.5, cy:0.5, r:0.5},
                stops: [
                  [0.5, '#000'],
                  [0.75, '#fff'],
                  [1, '#000']
                ]
              },
              borderWidth: 0,
              outerRadius: '100%'
            }
          }, 
          title: {
            text: Ps[0].repr + " vs " + Ps[1].repr
          },
          subtitle: {
            text: typeof(r)==='number' ? rMsg + r.toFixed(2) : r
          },
          legend: {
            align: 'right',
            verticalAlign: 'middle'
          },
          xAxis: xAxis,
          yAxis: yAxis,
          tooltip: {
            formatter: function() {
              if (Ps[0].type === 'circ') {
                var X = this.x + " °";
              }
              else if (Ps[0].type === 'circ_cat') {
                var X = Ps[0].maps.cat_tooltip[this.x];
              }
              else if (Ps[0].type === 'time') {
                var HHMM = hhmm(this.x);
                var X = HHMM[0] + ":" + HHMM[1];
              };
              if (Ps[1].type === 'circ') {
                var Y = this.y + " °";
              }
              else if (Ps[1].type === 'circ_cat') {
                var Y = Ps[1].maps.cat_tooltip[Ps[1].maps.categories[this.y]];
              }
              else if (Ps[1].type === 'time') {
                var HHMM = hhmm(this.y);
                var Y = HHMM[0] + ":" + HHMM[1];
              }
              return "<b>" + this.point.name + "</b><br/>" + Ps[0].repr + ": <b>" + X + "</b><br/>" + Ps[1].repr + ": <b>" + Y + "</b>";
            }
          },
          series: series
        };
      } // else if (chartType === 'torus')

      // chartType === 'rect' {{{4
      else {
        function titleText(P) {
          var T = P.repr;
          if (P.measure) {T += ', ' + P.measure}
          return T;
        }

        // xAxis
        var xAxis;
        if (Ps[0].type === 'bool') {
          xAxis = {
            title: {
              text: titleText(Ps[0])
            },
            min: 0,
            max: 1,
            tickInterval: 1,
            startOnTick: true,
            endOnTick: true,
            labels: {
              formatter: function() {return this.value===0 ? _('Ложь') : _('Истина')}
            }
          }
        }
        else {
          xAxis = {
            title: {
              text: titleText(Ps[0])
            },
            maxPadding: 0.02,
            minPadding: 0.02,
            endOnTick: false,
            startOnTick: false,
            gridLineWidth: 1,
            gridLineColor: "#E0E0E0",
            gridLineDashStyle: "dash"
          };
        }
        // yAxis
        var yAxis;
        if (Ps[1].type === 'bool') {
          yAxis = {
            title: {
              text: titleText(Ps[1])
            },
            categories: [_('Ложь'), _('Истина')],
            min: 0,
            max: 1,
            startOnTick: true,
            endOnTick: true,
            tickmarkPlacement: 'on'
          }
        }
        else {
          yAxis = {
            title: {
              text: titleText(Ps[1])
            },
            maxPadding: 0.02,
            minPadding: 0.02,
            endOnTick: false,
            startOnTick: false,
          }
        }

        // Объект графика
        var Chart = {
          chart: {
            width: 960,
            height: 960
          },
          title: {
            text: Ps[0].repr + " vs " + Ps[1].repr
          },
          subtitle: {
            text: typeof(r)==='number' ? rMsg + r.toFixed(2) : r
          },
          legend: {
            align: 'right',
            verticalAlign: 'middle'
          },
          xAxis: xAxis,
          yAxis: yAxis,
          tooltip: {
            formatter: function() {
              var X, Y
              if (Ps[0].type === 'duration') {
                var HHMM = hhmm(this.x);
                X = HHMM[0] + _('ч ') + HHMM[1] + _('мин');
              }
              else if (Ps[0].type === 'bool') {
                var X = this.x===0 ? _('Ложь') : _('Истина');
              }
              else {
                X = this.x
                if (Ps[0].measure) {
                  X += " " + Ps[0].measure;
                }
              };
              if (Ps[1].type === 'duration') {
                var HHMM = hhmm(this.y);
                Y = HHMM[0] + _('ч ') + HHMM[1] + _('мин');
              }
              else if (Ps[1].type === 'bool') {
                var Y = this.y===0 ? _('Ложь') : _('Истина');
              }
              else {
                Y = this.y
                if (Ps[1].measure) {
                  Y += " " + Ps[1].measure;
                }
              };
              return "<b>" + this.point.name + "</b><br/>" + Ps[0].repr + ": <b>" + X + "</b><br/>" + Ps[1].repr + ": <b>" + Y + "</b>";
            }
          },
          series: series
        };
      } // else (chartType === 'cylinder')
    } // else (pNames[0]==='date' || pNames[1]==='date')
  } // else (cbsLen === 1)

  // Отрисовка графика {{{2
  container.highcharts(Chart);
  document.location.href = '#chart';
  console.timeEnd('chart');
}


//function buildDefaultChart() {{{1
function buildDefaultChart() {
  // Ищем пару наиболее коррелирующих параметров, один из которых обязательно пользовательский.
  var corrMatrix = DATA.corrMatrix;
  var props = []; // [prop1, prop2]
  var maxCorr = 0; // модуль
  for (var rowProp in corrMatrix) {
    if (rowProp in DATA.uProps) {
      var row = corrMatrix[rowProp];
      for (var colProp in row) {
        var corr = Math.abs(row[colProp].value);
        if (corr > maxCorr) {
          props = [rowProp, colProp];
          maxCorr = corr;
        }
      }
    }
  }
  // Отмечаем эти параметры в форме при графике и нажимаем кнопку "Построить график".
  var cbs = $QA('#props4charts input[type="checkbox"]');
  for (var i=0; i<cbs.length; i++) {
    var cb = cbs[i];
    if (cb.value===props[0] || cb.value===props[1]) {
      cb.click();
    }
  }
  $I('drawChart').click();
}


//function buildTables() {{{1
function buildTables() {
  buildDatatable();
  buildStattable();
  buildCorrtable();
}

//function buildPhrases() {{{1
function buildPhrases() {
  // Каждому пользовательскому параметру добавляем свойство 'phrase' (строка, массив или двумерный массив).
  var corrMatrix = DATA.corrMatrix;
  for (var rowProp in corrMatrix) {
    // Фразы придумываем только для пользовательских параметров.
    if (rowProp in DATA.uProps) {
      var values=[], significances=[], scales=[];
      var row = corrMatrix[rowProp];
      for (var colProp in row) {
        var corr = row[colProp];
        values.push(corr.value);
        significances.push(corr.significant);
        scales.push(corr.scale);
      }
      // 1.Все значения null => недостаточно данных
      if (values.every(function(v) {return (v===null);})) {
        DATA.uProps[rowProp].phrase = _('недостаточно данных');
      }
      // 2.Значимых коэффициентов корреляции нет
      else if (significances.every(function(s) {return (s===false);})) {
        DATA.uProps[rowProp].phrase = _('значимых связей не выявлено');
      }
      // 3.Все коэффициенты корреляции слабые
      else if (scales.every(function(s) {return (s===null);})) {
        DATA.uProps[rowProp].phrase = _('значимых связей не выявлено');
      }
      // 4.Есть чёткие зависимости
      else if (scales.indexOf('high')!==-1 || scales.indexOf('very_high')!==-1) {
        var highCorrs = [];
        for (var colProp in row) {
          var corr = row[colProp];
          if ((corr.scale==='high' || corr.scale==='very_high') && corr.significant===true) {
            highCorrs.push([colProp, corr.value, corr.scale]);
          }
        }
        if (highCorrs.length > 0) {
          // сортировка по убыванию значения
          highCorrs.sort(function(a,b) {return (Math.abs(b[1])-Math.abs(a[1]));});
          DATA.uProps[rowProp].phrase = highCorrs;
        }
        else {
          console.error('Unexpected situation with highCorrs in buildSummary');
          DATA.uProps[rowProp].phrase = _('значимых связей не выявлено');
        }
      }
      // 5.Есть слабые или средние зависимости
      else if (scales.indexOf('weak')!==-1 || scales.indexOf('medium')!==-1) {
        var mediumCorrs = [];
        for (var colProp in row) {
          var corr = row[colProp];
          if ((corr.scale==='weak' || corr.scale==='medium') && corr.significant===true) {
            mediumCorrs.push([colProp, corr.value, corr.scale]);
          }
        }
        if (mediumCorrs.length > 0) {
          // берём 1, у которого наибольшее по модулю значение
          var maxCorr = mediumCorrs[0];
          for (var i=1; i<mediumCorrs.length; i++) {
            if (Math.abs(mediumCorrs[i][1]) > Math.abs(maxCorr[1])) {
              maxCorr = mediumCorrs[i];
            }
          }
          DATA.uProps[rowProp].phrase = maxCorr;
        }
        else {
          console.error('Unexpected situation with mediumCorrs in buildSummary');
          DATA.uProps[rowProp].phrase = _('значимых связей не выявлено');
        }
      }
    }
  }
}

//function buildSummary() {{{1
function buildSummary() {
  var container = $I('summary');

  var html = _('<h2>Краткая сводка по показателям:</h2>');
  html += '<ul>';
  for (var i=0; i<DATA.uPropsOrder.length; i++) {
    var prop = DATA.uProps[DATA.uPropsOrder[i]];
    html += '<li><b>'+prop.repr+':</b> '+formatPhrase(prop.phrase)+'</li>';
  }
  html += '</ul>';

  container.innerHTML = html;
}

//function toggleDatatable() {{{1
function toggleDatatable() {
  if (this.className === 'active') {
    $I('datatableWrapper').classList.add('hidden');
    this.innerHTML = _('Показать таблицу с данными');
    this.className = '';
  }
  else {
    showOnlyOne('datatableWrapper');
    this.innerHTML = _('Скрыть таблицу с данными');
    this.className = 'active';
  }
}

//function toggleStattable() {{{1
function toggleStattable() {
  if (this.className === 'active') {
    $I('stattableWrapper').classList.add('hidden');
    this.innerHTML = _('Показать статистические показатели');
    this.className = '';
  }
  else {
    showOnlyOne('stattableWrapper');
    this.innerHTML = _('Скрыть статистические показатели');
    this.className = 'active';
  }
}

//function toggleCorrtable() {{{1
function toggleCorrtable() {
  if (this.className === 'active') {
    $I('corrtableWrapper').classList.add('hidden');
    this.innerHTML = _('Показать корреляционную таблицу');
    this.className = '';
  }
  else {
    showOnlyOne('corrtableWrapper');
    this.innerHTML = _('Скрыть корреляционную таблицу');
    this.className = 'active';
  }
}

//function toggleChart() {{{1
function toggleChart() {
  if (this.className === 'active') {
    $I('chartWrapper').classList.add('hidden');
    this.innerHTML = _('Показать график');
    this.className = '';
  }
  else {
    showOnlyOne('chartWrapper');
    this.innerHTML = _('Скрыть график');
    this.className = 'active';
  }
}

//function toggleForm() {{{1
function toggleForm() {
  if (this.hasAttribute('oldText')) {
    this.parentNode.nextElementSibling.classList.add('hidden');
    this.innerHTML = this.getAttribute('oldText');
    this.removeAttribute('oldText');
    this.setAttribute('title', _('Нажмите, чтобы появилась форма, в которой можно выбрать параметры, которые будут отображаться в таблице (на графике)'));
  }
  else {
    this.parentNode.nextElementSibling.classList.remove('hidden');
    this.setAttribute('oldText', this.innerHTML);
    this.innerHTML = _('Скрыть форму');
    this.setAttribute('title', _('Скрыть форму выбора параметров'));
  }
}

function table2file(tableId, format) { //{{{1
  // Через ajax это сделать нельзя, только через отправку формы. 
  // В случае firefox форма должна физически присутствовать в DOM.
  var table = $I(tableId)
  if (format === 'xlsx') {
    // Ширины столбцов
    var ths = table.getElementsByClassName('colnumbers')[0].cells;
    var colWidths = [];
    for (var i=0; i<ths.length; i++) {
      colWidths.push(ths[i].offsetWidth);
    }
    // Высоты строк
    $I('pagerToggle').click(); // отключение пагинации
    var trs = table.rows;
    var rowHeights = [];
    for (var i=0; i<trs.length; i++) {
      rowHeights.push(trs[i].offsetHeight);
    }
    $I('pagerToggle').click(); // включение пагинации
  }
  // html таблицы
  var tableContent = table.innerHTML;

  var form = $E('form');
  form.setAttribute('method', 'post');
  form.setAttribute('action', '/analysis_saved');

  var idInput = $E('input');
  idInput.setAttribute('type', 'text');
  idInput.setAttribute('name', 'tableId');
  idInput.value = tableId;
  form.appendChild(idInput);

  var textarea = $E('textarea');
  textarea.setAttribute('name', 'content');
  var content = $TN(tableContent);
  textarea.appendChild(content);
  form.appendChild(textarea);

  if (format === 'xlsx') {
    var widthsInput = $E('input');
    widthsInput.setAttribute('type', 'text');
    widthsInput.setAttribute('name', 'widths');
    widthsInput.value = colWidths.join(',');
    form.appendChild(widthsInput);

    var heightsInput = $E('input');
    heightsInput.setAttribute('type', 'text');
    heightsInput.setAttribute('name', 'heights');
    heightsInput.value = rowHeights.join(',');
    form.appendChild(heightsInput);
  }

  var formatInput = $E('input');
  formatInput.setAttribute('type', 'text');
  formatInput.setAttribute('name', 'format');
  formatInput.value = format;
  form.appendChild(formatInput);

  var submit = $E('input');
  submit.setAttribute('type', 'submit');
  submit.setAttribute('name', 'submit');
  submit.setAttribute('value', 'table2file');
  form.appendChild(submit);

  $I('table2file').innerHTML = '';
  $I('table2file').appendChild(form);
  submit.click();
}
function doAnalysis() { //{{{1
  // Дозаполнение данных, заполнение страницы {{{2
  buildData();
  buildForms();
  buildTables();
  if ('uProps' in DATA) {
    buildDefaultChart();
    buildPhrases();
    buildSummary();
  }

  // Pager {{{2
  pagerToggle();
  
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
  $I('stattable2csv').onclick = function() {table2file('statTable', 'csv');};
  $I('corrtable2csv').onclick = function() {table2file('corrTable', 'csv');};
  $I('datatable2csv').onclick = function() {table2file('dataTable', 'csv');};
  $I('stattable2xlsx').onclick = function() {table2file('statTable', 'xlsx');};
  $I('corrtable2xlsx').onclick = function() {table2file('corrTable', 'xlsx');};
  $I('datatable2xlsx').onclick = function() {table2file('dataTable', 'xlsx');};
}
//}}}

