## Inherit {{{1
<%inherit file="base.mako"/>

## Block Title {{{1
<%block name="Title">${_(u'Анализ тестовых данных')}</%block>

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
 <script src="/js/jquery.csv-0.71.min.js"></script>
 <script src="/js/analysis_test.js"></script>
 <script src="/js/analysis_datatable.js"></script>
</%block>

## Block Style {{{1
<%block name="Style">
<style>
ul.reqs {
  list-style-type: disc;
  margin-left: 20px;
}
#file { /* hack for opera */
  width: 0px;
  height: 0px;
  opacity: 0;
}
#warning table {
  border: 1px solid red;
}
#warning table th, #warning table td {
  border: 1px solid red;
  padding: 3px;
}
</style>
</%block>

## Block Content {{{1
<%block name="Content">
## noscript {{{2
<noscript><div class="js_required">${_(u'Внимание! Эта страница для своей работы требует включённый javascript.')}</div></noscript>

## div#instructions {{{2
<button id="toggleInstructions">${_(u'Скрыть инструкции')}</button>
<div id="instructions">
 <p>${_(u'На этой странице вы можете загрузить и проанализировать ваши данные. В настоящий момент загрузка данных может осуществляться только с помощью файлов в формате <a href="http://ru.wikipedia.org/wiki/CSV" target="_blank">csv</a>. Максимальный размер файла &mdash; 100 кб. Чтобы выбрать файл, нажмите на кнопку "Загрузить файл с данными".')}</p>
 <p><b>${_(u'Требования к формату файла:')}</b>
  <ul class="reqs">
   <li>${_(u'Значения отдельных колонок разделяются точкой с запятой (;).')}</li>
   <li>${_(u'Первая строка - заголовок;')}</li>
   <li>${_(u'Значения первой колонки - даты в формате дд.мм.гггг (22.06.2013);')}</li>
  </ul>
 </p>
 <p><b>${_(u'Требования к формату заголовка:')}</b></p>
 <p>${_(u'Поля заголовка должны быть представлены в формате "&lt;название параметра&gt;,&lt;тип данных&gt;", например "age,int" или в случае шкалового показателя в формате "&lt;название параметра&gt;,scale,[&lt;минимальное значение&gt;, &lt;максимальное значение&gt;, &lt;шаг шкалы&gt;]", например "grade,scale,[2,5,1]". Первое поле &mdash; это дата, поэтому игнорируется. В данное время поддерживаются только числовые (целые числа (int) и числа с плавающей точкой (float)), булевы (bool), шкаловые (scale) и временные (time) данные. Тип соответствующих данных указывается в заголовке после названия показателя через запятую. Если тип не указан, то по-умолчанию он является числом с плавающей точкой (float).')}</p>
 <p><b>${_(u'Требования к формату значений:')}</b></p>
 <p>${_(u'Все значения в конкретном столбце должны соответствовать типу, указанному в заголовке. Значение может отсутствовать, быть пустым. Для ввода пустого значения надо либо место между разделителями (;) оставить пустым, либо ввести туда значение "--".')}</p>
 <p><b>${_(u'Типы данных:')}</b>
  <ul class="reqs">
   <li>${_(u'Целые числа (int): поддерживаются целые числа.')}</li>
   <li>${_(u'Числа с плавающей точкой (float): поддерживаются целые числа и числа с десятичной дробью. В качестве разделителя может использоваться  только точка (.).')}</li>
   <li>${_(u'Булевы значения: поддерживаются значения "true", "false", 0, 1, "+", "-", "да", "нет".')}</li>
   <li>${_(u'Шкаловые значения: целые числа. Нижняя и верхняя границы диапазона значений указываются в заголовке после типа через запятую в формате [минимум, максимум, шаг] ([0,10,1]).')}</li>
   <li>${_(u'Временные значения записываются в формате ЧЧ:ММ (05:09).')}</li>
   <li>${_(u'Чтобы обозначить пропуск в значениях, можно оставить пустое место между точками с запятой(;;), либо ввести строку "--" (;--;).')}</li>
  </ul>
 </p>
 <p>${_(u'Файл CSV можно создать вручную или сохранить лист Excel как файл csv и выбрать в качестве разделителя точку с запятой (;).')} <a href="/doc/csv_example.csv">${_(u'Пример файла')}</a></p>
</div>

## upload button {{{2
<p>
 <input type="file" id="file" accept="text/comma-separated-values" />
 <button id="fileSelect" type="button">${_(u'Загрузить файл с данными')}</button>
 <span id="fileSelected">${_(u'файл не выбран')}</span>
</p>
<div class="warnings" id="warning"></div>
<div class="warnings" id="wait"></div>

## div#analysis {{{2
<div id="analysis" class="hidden">
 ## div#summary {{{3
 <div id="summary"></div>
 
 ## div#buttons {{{3
 <div id="buttons">
  <button id="toggleChart" type="button" name="toggleChart">${_(u'Показать график')}</button>
  <button type="button" name="toggleStattable" id="toggleStattable">${_(u'Показать статистические показатели')}</button>
  <button type="button" name="toggleCorrtable" id="toggleCorrtable">${_(u'Показать корреляционную таблицу')}</button>
  <button type="button" name="toggleDatatable" id="toggleDatatable">${_(u'Показать таблицу с данными')}</button>
 </div>
 
 ## div#chartWrapper {{{3
 <div id="chartWrapper" class="tableWrapper hidden">
  <div>
   <button class="propsSelect">${_(u'Выбрать параметры для построения графика')}</button>
  </div>
  <div id="props4charts" class="propsDiv hidden"></div>
  <a name="chart"></a>
  <div id="chartContainer"></div>
 </div>
 
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

 ## div#table2file {{{3
 ## В этот div помещаем временную форму из функции table2file.
 <div id="table2file" class="hidden"></div>
</div>

## script {{{3
<script>
lang = '${lang}';
</script>

</%block>
