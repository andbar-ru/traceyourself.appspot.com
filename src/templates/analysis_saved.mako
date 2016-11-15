## Inherit {{{1
<%inherit file="base.mako"/>
##}}}
## Block Title {{{1
<%block name="Title">${_(u'Анализ сохранённых данных')}</%block>
##}}}
## Block Links {{{1
<%block name="Links">
 <link rel="stylesheet" href="/css/dateinput.css"/>
 <link rel="stylesheet" href="/css/analysis.css"/>
 <script src="/js/jquery.tablesorter.min.js"></script>
 <script src="/js/jquery.tablesorter.pager.min.js"></script>
 <script src="/js/tablesorter_extra.js"></script>
 <script src="/js/jquery.tools.min.js"></script>
 <script src="/js/highcharts.src.js"></script>
 <script src="/js/highcharts-more.src.js"></script>
 <script src="/js/highcharts-exporting.js"></script>
 <script src="/js/student_table.js"></script>
 <script src="/js/stat_functions.js"></script>
 <script src="/js/analysis_functions.js"></script>
 <script src="/js/analysis_datatable.js"></script>
</%block>
##}}}
## Block Content {{{1
<%block name="Content">
## noscript {{{2
<noscript><div class="js_required">${_(u'Внимание! Эта страница для своей работы требует включённый javascript.')}</div></noscript>
##}}}
## p.warnings {{{2
<p id="warnings" class="warnings">${_(u'Подождите, загружаются данные...')}</p>
##}}}
## div#analysis {{{2
<div id="analysis" class="hidden">
 ## div#summary {{{3
 <div id="summary"></div>
 ##}}}
 ## div#buttons {{{3
 <div id="buttons">
  <button id="toggleChart" type="button" name="toggleChart">${_(u'Показать график')}</button>
  <button type="button" name="toggleStattable" id="toggleStattable">${_(u'Показать статистические показатели')}</button>
  <button type="button" name="toggleCorrtable" id="toggleCorrtable">${_(u'Показать корреляционную таблицу')}</button>
  <button type="button" name="toggleDatatable" id="toggleDatatable">${_(u'Показать таблицу с данными')}</button>
 </div>
 ##}}}
 ## div#chartWrapper {{{3
 <div id="chartWrapper" class="tableWrapper hidden">
  <div>
   <button class="propsSelect">${_(u'Выбрать параметры для построения графика')}</button>
  </div>
  <div id="props4charts" class="propsDiv hidden"></div>
  <a name="chart"></a>
  <div id="chartContainer"></div>
 </div>
 ##}}}
 ## div#stattableWrapper {{{3
 <div id="stattableWrapper" class="tableWrapper hidden">
  <div>
   <button class="propsSelect">${_(u'Выбрать параметры для отображения в таблице')}</button>
   <button class="tablePopup">${_(u'Показать таблицу в отдельном окне')}</button>
   <button id="stattable2csv">${_(u'Скачать таблицу в формате CSV')}</button>
   <button id="stattable2xlsx">${_(u'Скачать таблицу в формате XLSX')}</button>
  </div>
  <div id="props4statTable" class="propsDiv hidden"></div>
  <div class="tableContainer" id="stattableContainer"></div>
 </div>
 ##}}}
 ## div#corrtableWrapper {{{3
 <div id="corrtableWrapper" class="tableWrapper hidden">
  <div>
   <button class="propsSelect">${_(u'Выбрать параметры для отображения в таблице')}</button>
   <button class="tablePopup">${_(u'Показать таблицу в отдельном окне')}</button>
   <button id="corrtable2csv">${_(u'Скачать таблицу в формате CSV')}</button>
   <button id="corrtable2xlsx">${_(u'Скачать таблицу в формате XLSX')}</button>
  </div>
  <div id="props4corrTable" class="propsDiv hidden"></div>
  <div class="tableContainer" id="corrtableContainer"></div>
 </div>
 ##}}}
 ## div#datatableWrapper {{{3
 <div id="datatableWrapper" class="tableWrapper hidden">
  <div>
   <button class="propsSelect">${_(u'Выбрать параметры и даты для отображения в таблице')}</button>
   <button class="tablePopup">${_(u'Показать таблицу в отдельном окне')}</button>
   <button id="pagerToggle">${_(u'Отключить разбиение на страницы')}</button>
   <button id="datatable2csv">${_(u'Скачать таблицу в формате CSV')}</button>
   <button id="datatable2xlsx">${_(u'Скачать таблицу в формате XLSX')}</button>
  </div>
  <div id="props4dataTable" class="propsDiv hidden"></div>
  <div class="tableContainer" id="datatableContainer"></div>
 </div>
 ##}}}
 ## div#table2file {{{3
 ## В этот div помещаем временную форму из функции table2file.
 <div id="table2file"></div>
 ##}}}
</div>
##}}}
## script {{{2
<script>
var DATA;
$.getJSON('/get_data')
  .done(function(data) {
    DATA = data;
    $I('warnings').innerHTML = '';
    doAnalysis();
    $I('analysis').classList.remove('hidden');
  })
  .fail(function() {
    $I('warnings').innerHTML = 'ОШИБКА! Не удалось загрузить данные.';
  });
lang = '${lang}';
</script>
##}}}
</%block>
##}}}
