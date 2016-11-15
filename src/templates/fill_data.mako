## Функции, специфичные для страницы
##<%inherit file="base.mako"/> {{{1
<%inherit file="base.mako"/>

##Block Title {{{1
<%block name="Title">${_(u'Заполнение параметров')}</%block>

##Block Links {{{1
<%block name="Links">
 <link rel="stylesheet" href="/css/dateinput.css"/>
 <script src="/js/js_extra.js"></script>
 <script src="/js/jquery.tools.min.js"></script>
 <script src="/js/fill_data.js"></script>
 <script src="/js/location.js"></script>
</%block>

##Block Style {{{1
<%block name="Style">
<style>
#content ul {
	margin-bottom: 10px;
}
#locationForm {
	display: none;
	background-color: #d1d1d1;
	padding: 5px;
	margin: 5px 0;
	border-radius: 5px;
}
</style>
</%block>

##Block Content {{{1
<%block name="Content">

<p class="warnings">
 % for W in WARNINGS:
  ${W}<br/>
 % endfor
</p>

<p>${_(u'Текущее место пребывания:')} <b>${residence}</b> <button id="toggleLocationForm" type="button">Изменить</button></p>
<div id="locationForm">
 ${locationForm.render(withAnchor=(True if action=='editLocation' else False), action=action_url, method="post")}
</div>

% if form.data:
 ${form.render(action=action_url, method="post")}
% else:
 <p class="warnings">${_(u'У вас нет параметров, создать их можно')} <a href="/prof">${_(u'здесь')} >>></a>.</p>
% endif

<script>
lang = '${lang}';
</script>

</%block>
