## Функции, специфичные для страницы
##<%def name="common_props_form()"> {{{1
<%def name="common_props_form()">
<% form = forms['commonPropsForm'] %>
<form name="common_props" action="${action_url}" method="post">
 <p class="note">${_(u'Отметьте те из них, которые должны учитываться при анализе')}</p>
 <p><b>${_(u'Экономические индикаторы')}:</b></p>
 <div style="margin-left:20px;">
  <p><b>${form.indiceProps.label}:</b></p>
  ${form.indiceProps}
  <p><b>${form.commodityProps.label}:</b></p>
  ${form.commodityProps}
  <p><b>${form.currencyProps.label}:</b></p>
  ${form.currencyProps}
 </div>
 <p><b>${form.astroProps.label}:</b> <span class="note">(${_(u'Прямое восхождение, склонение и расстояние от Земли по каждому объекту')})</span></p>
 ${form.astroProps}
 <p><b>${form.geomagneticProps.label}:</b></p>
 ${form.geomagneticProps}
 <p><b>${form.weatherProps.label}:</b></p>
 ${form.weatherProps}
 <p>${form.submitCommonProps}</p>
</form>
</%def>

##<%def name="add_prop_form(form=None)"> {{{1
<%def name="add_prop_form(form=None)">
% if form is None:
 <% form = forms['add_prop_form'] %>
% else:
 <a name="add_prop"></a>
% endif
<p><strong>${_(u'Добавление параметра')}</strong></p>
<form class="details" name="add_prop" action="${action_url}" method="post">
 ${render_field(form.name, size="50")}
 <div>${render_field(form.comment, wrapper_='span', field_wrapper_='div', cols="100", rows="5")}</div>
 ${render_field(form.type)}
 <div id="measure_field">
  ${render_field(form.measure, size=10)}
  <p class="note">${form.measure.description}</p>
 </div>
 <div id="scale_attrs_field" title="${_(u'Используется только с типом `Шкала`')}">
  ${form.scale_attrs_field.label}:<br/>
  ${render_field_errors(form.scale_attrs_field, errors=['errors_'])}
  % for subfield in form.scale_attrs_field:
	 ${render_field(subfield, size=4, wrapper_='span', delimiter_=' ')}
  % endfor
  <p class="note">${form.scale_attrs_field.description}</p>
 </div>
 ${render_field(form.submit_add_prop, show_label_=False)}
 <div>${_(u'Звёздочкой (<span class="required">*</span>) отмечены поля, обязательные для заполнения')}</div>
</form>
</%def>

##<%def name="prop_edit_form(prop=None, form=None)"> {{{1
<%def name="prop_edit_form(prop=None, form=None)">
% if form is None:
 <% form = forms['prop_edit_forms'][prop.key().id()] %>
% else:
 <a name="edit_prop"></a>
% endif
<form class="details" name="prop_details" action="${action_url}" method="post">
 ${render_field(form.name, size="50")}
 <div>${render_field(form.comment, wrapper_='span', field_wrapper_='div', cols="100", rows="5")}</div>
 ${render_field(form.order, size=1)}
 ${render_field(form.type, field_content=select_type(form.type))}
 <div id="measure_field">
	${render_field(form.measure, size=10)}
	<p class="note">${form.measure.description}</p>
 </div>
 <div id="scale_attrs_field" title="${_(u'Используется только с типом `Шкала`')}">
	${form.scale_attrs_field.label}:<br/>
	${render_field_errors(form.scale_attrs_field, errors=['errors_'])}
	% for subfield in form.scale_attrs_field:
	 ${render_field(subfield, size=4, wrapper_='span', delimiter_=' ')}
	% endfor
	<p class="note">${form.scale_attrs_field.description}</p>
 </div>
 ${form.submit_edit_prop}
 ${form.delete_prop(class_='dangerous', onclick=_(u'return confirm("Вы действительно хотите удалить параметр?")'), style='margin-left:100px')}
 <div>${_(u'Звёздочкой (<span class="required">*</span>) отмечены поля, обязательные для заполнения')}</div>
</form>
</%def>

##<%namespace module="templates.functions" import="render_field, render_field_errors, select_type"/> {{{1
<%namespace module="templates.functions" import="render_field, render_field_errors, select_type"/>

##<%inherit file="base.mako"/> {{{1
<%inherit file="base.mako"/>

## Block Title {{{1
<%block name="Title">${title}</%block>

## Block Links {{{1
<%block name="Links">
 <script src="/js/profile.js"></script>
 <script src="/js/location.js"></script>
</%block>

## Block Style {{{1
<%block name="Style">
<style type="text/css">
#static div {
	margin-bottom: 10px;
}
#static_data, #common_props_div {
	display: none;
	padding: 5px;
	background-color: #ccccff;
	border-radius: 5px;
}
h4 {
	margin-top: 20px;
	margin-bottom: 10px;
}
h4, h5 {
	padding-left: 5px;	
}
li.prop {
	padding: 5px;
	margin-bottom: 3px;
	min-height: 24px;
	background: #ccccff;
	border-radius: 5px;
}
li.prop a {
	line-height: 24px;
}
li.prop a:hover {
	text-decoration: underline;
}
div.info {
	margin-right: 30px;
	min-height: 24px;
	cursor: pointer;
}
button.fold, button.unfold {
	display: block;
	float: right;
	border: none;
	background-color: transparent;
	cursor: pointer;
	padding: 0;
	width: 24px;
	height: 24px;
}
div.details {
  display: none;
	background-color: #d1d1d1;
	padding: 5px;
}
form.details>div {
	margin: 5px 0px 5px;
}
button.unfold {
	background-image: url("/img/unfold.png");
}
button.fold {
	background-image: url("/img/fold.png");
}
option[value="ALL"] {
  font-weight: bold;
}
</style>
</%block>

## Block Content {{{1
<%block name="Content">
 ## noscript {{{2
 <noscript>
  <div class="js_required">${_(u'Внимание! Эта страница для своей работы требует включённый javascript.')}</div>
 </noscript>

 ## if U: {{{2
 % if U:
  ## div#static_data {{{3
  <h4>${_(u'Данные вашего профиля:')}&nbsp;<input id="toggle_static_data" type="button" value="${_(u'Явить')}" /></h4>
  <div id="static_data">
   <p>email: <b>${U.key().name()}</b></p>
   <p>${_(u'Имя')}: <b>${U.surname and U.surname or ''} ${U.name and U.name or ''} ${U.patronymic and U.patronymic or ''}</b></p>
   <p>${_(u'Пол')}: <b>${U.gender=='M' and u'Мужской' or (U.gender=='F' and u'Женский' or '')}</b></p>
   <p>${_(u'Дата рождения')}: <b>${U.birthdate.strftime("%d.%m.%Y") if U.birthdate else ''}</b></p>
   <p>${_(u'Место пребывания')}: <b>${U.residence.name}</b></p>
   <div><button id="toggleEditStatic" type="button" name="edit_static">${_(u'Редактировать личные данные')}</button></div>
   <div id="editStaticDiv" class="details">
    % if action == 'edit_static':
     ${form.render(edit=True, locality=U.residence.name, withAnchor=True, class_='details', name='edit_static', action=action_url, method='post')}
    % else:
     ${forms['profileForm'].render(edit=True, locality=U.residence.name, class_='details', name='edit_static', action=action_url, method='post')}
    % endif
   </div>
  </div>
 
  ## div#common_props_div {{{3
  <h4>${_(u'Общие параметры')}:&nbsp;<input id="toggle_common_props" type="button" value="${_(u'Явить')}" /></h4>
  <div id="common_props_div">
   ${common_props_form()}
  </div>

  ## div#user_props_div {{{3
  <h4>${_(u'Параметры пользователя')} (${props.count()} ${_(u'из')} ${U.propsLimit}):</h4>
  <div id="user_props_div">
   ## Если параметров нет
   % if props.count() == 0:
    <h4>${_(u'Необходимо добавить пользовательские параметры')}!</h4>
   % endif
   ## Список параметров
   <ul> 
    % for prop in props:
     <li class="prop">
			<button type="button" class="unfold" name="toggle_fold" title="${_(u'Развернуть')}"></button>
      <div class="info">
       <a name="${prop.key().id()}" rel="details">${prop.name}</a>
       <span class="note">(${prop.type})</span>
      </div>
      <div class="details clear">
       % if action == 'edit_prop' and form.current_prop_name == prop.name:
        ${prop_edit_form(form=form)}
       % else:
        ${prop_edit_form(prop)}
       % endif
      </div>
     </li>
    % endfor
   </ul>
   <div>
    % if props.count() >= U.propsLimit:
     <p class="warnings">${_(u'Вы не можете создать больше %d параметров. Для увеличения количества свяжитесь с разработчиком сайта.') % U.propsLimit} <a href="/contacts">&gt;&gt;&gt;</a></p>
     <button name="add_prop" type="button" disabled>${_(u'Добавить параметр')}</button>
    % else:
     <button name="add_prop" type="button">${_(u'Добавить параметр')}</button>
    % endif
    <!-- Удалить все параметры -->
    % if props.count() > 0:
     <form method="post" action="${action_url}" style="display:inline">
      <button class="dangerous" style="margin-left:100px" name="delete_all_props" type="submit" value="1" onclick="${_(u'return confirm(\'Вы уверены? Все ваши данные будут удалены.\')')}">${_(u'Удалить все параметры')}</button>
     </form>
    % endif #if props.count() > 0
   </div>
   <div id="addPropDetails" class="details">
    % if action == 'add_prop':
     <div id="add_prop_div">${add_prop_form(form)}</div>
    % else:
     <div id="add_prop_div">${add_prop_form()}</div>
    % endif
   </div>
  </div>

 ## else (if U) {{{2
 ## Нет аккаунта, предоставляем форму для заполнения личных данных
 % else: #if U
  <p>${_(u'Чтобы начать пользоваться сайтом, нужно заполнить данные о себе и создать профиль.')}</p>
   % if form is None:
    ${forms['profileForm'].render(class_='details', name='edit_static', action=action_url, method='post')}
   % else:
    ${form.render(class_='details', name='edit_static', action=action_url, method='post')}
   % endif
 % endif #if U
</%block>
