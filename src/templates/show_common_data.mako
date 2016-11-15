<html>
## <head> {{{1
<head>
<link rel="stylesheet" href="/css/analysis.css"/>
<link rel="stylesheet" href="/css/dateinput.css"/>
<script type="text/javascript" src="/js/jquery-1.7.2.min.js"></script>
<script>var lang = "${lang}";</script>
<script src="/js/jed.js"></script>
<script src="/js/locale/${lang}/messages.js"></script>
<script type="text/javascript" src="/js/udf.js"></script>
<script type="text/javascript" src="/js/show_common_data.js"></script>
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

<title>Данные общих показателей</title>
<style>
body, button, select, input {
  color: #333333;
  font: 10pt "Liberation Sans", sans-serif;
}
form {
  background-color: #e6e6e6;
  padding: 10px 10px 0 10px;
  border: 1px solid #cccccc;
  border-radius: 5px;
}
.error {
  color: red;
}
.asterisk, .hidden {
  display: none;
}
.required .asterisk {
  color: red;
  display: inline;
}
.js_required {
	background-color: red;
	color: white;
	font-weight: bold;
	padding: 10px;
}
.note {
  color: gray;
  font-size: 8pt;
}
#mainFormToggle {
  margin: 0 0 -1px 20px;
  padding: 3px 10px;
  border: 3px outset #cccccc;
  border-bottom: 1px solid #e6e6e6;
  border-radius: 5px 5px 0 0;
  background: #ffffff;
  cursor: pointer;
}
table {
  border-collapse: collapse;
  font: 10pt "Liberation Sans", sans-serif;
}
td, th {
  border: 1px solid #333333;
  padding: 3px;
  vertical-align: top;
}
ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}
button[name="selectAll"] {
  margin-top: 10px;
}
</style>
</head>
##}}}
## <body> {{{1
<body>
<noscript><div class="js_required">${_(u'Внимание! Эта страница для своей работы требует включённый javascript.')}</div></noscript>
## mainForm {{{2
<button id="mainFormToggle">${_(u'Скрыть форму')}</button>
<div id="mainFormWrapper">
 <form id="commonDataForm">
  <div>${_(u'Выберите показатели, по которым нужно провести анализ, и диапазон дат, за которые выбирать данные. Если выбираете погодные показатели, то не забудьте выбрать населённый пункт.')}</div>
  <p id="residenceWrapper">
   ${commonDataForm.residence.label}:<span class="asterisk">*</span>
   ${commonDataForm.residence}
   <span id="residenceError" class="error"></span>
  </p>
  <p class="note">${_(u'Поле "Населённый пункт" становится обязательным, если выбирается хотя бы один показатель из группы "Данные погоды".')}</p>
  <p>
   ${_(u'Даты:')}
   <span class="required">${commonDataForm.dateFrom.label}<span class="asterisk">*</span>&nbsp;${commonDataForm.dateFrom}</span>
   <span class="required">${commonDataForm.dateTo.label}<span class="asterisk">*</span>&nbsp;${commonDataForm.dateTo}</span>
   <span id="dateFromError" class="error"></span>
   <span id="dateToError" class="error"></span>
  </p>
  <p class="required">
   ${_(u'Показатели')}:<span class="asterisk">*</span>
   <span id="commonPropertiesError" class="error"></span>
  </p>
  <table id="commonProperties">
   <thead>
    <tr>
     <th>${commonDataForm.indiceProps.label}</th>
     <th>${commonDataForm.commodityProps.label}</th>
     <th>${commonDataForm.currencyProps.label}</th>
     <th>${commonDataForm.astroProps.label}</th>
     <th>${commonDataForm.geomagneticProps.label}</th>
     <th>${commonDataForm.weatherProps.label}</th>
    </tr>
   </thead>
   <tbody>
    <tr>
     <td>
      ${commonDataForm.indiceProps}
      <button type="button" name="selectAll4mainForm">${_(u'Отметить все')}</button><br/>
      <button type="button" name="deselectAll4mainForm">${_(u'Снять отметку со всех')}</button>
     </td>
     <td>
      ${commonDataForm.commodityProps}
      <button type="button" name="selectAll4mainForm">${_(u'Отметить все')}</button><br/>
      <button type="button" name="deselectAll4mainForm">${_(u'Снять отметку со всех')}</button>
     </td>
     <td>
      ${commonDataForm.currencyProps}
      <button type="button" name="selectAll4mainForm">${_(u'Отметить все')}</button><br/>
      <button type="button" name="deselectAll4mainForm">${_(u'Снять отметку со всех')}</button>
     </td>
     <td>
      ${commonDataForm.astroProps}
      <button type="button" name="selectAll4mainForm">${_(u'Отметить все')}</button><br/>
      <button type="button" name="deselectAll4mainForm">${_(u'Снять отметку со всех')}</button>
     </td>
     <td>
      ${commonDataForm.geomagneticProps}
      <button type="button" name="selectAll4mainForm">${_(u'Отметить все')}</button><br/>
      <button type="button" name="deselectAll4mainForm">${_(u'Снять отметку со всех')}</button>
     </td>
     <td>
      ${commonDataForm.weatherProps}
      <button type="button" name="selectAll4mainForm" id="weatherSelectAll">${_(u'Отметить все')}</button><br/>
      <button type="button" name="deselectAll4mainForm" id="weatherDeselectAll">${_(u'Снять отметку со всех')}</button>
     </td>
    </tr>
   </tbody>
  </table>
  <p class="required">${_(u'Звёздочкой (<span class="asterisk">*</span>) отмечены поля, обязательные для заполнения или выбора.')}</p>
  <p>${commonDataForm.submit}</p>
  <p id="formErrors" class="error"></p>
 </form>
</div>
##}}}
## div#analysis {{{2
## Содержимое генерируется с помощью function initAnalysis.
<div id="analysisWrapper"></div>
##}}}
</body>
##}}}
</html>
