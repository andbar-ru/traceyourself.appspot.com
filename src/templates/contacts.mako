##<%inherit file="base.mako"/> {{{1
<%inherit file="base.mako"/>

## Block Title {{{1
<%block name="Title">${_(u'Контакты')}</%block>

## Block Style {{{1
<%block name="Style">
<style type="text/css">
form td {
  vertical-align: top;
}
</style>
</%block>

## Block Content {{{1
<%block name="Content">
<h1>${_(u'Контакты')}</h1>
<p>${_(u'По всем вопросам, пожеланиям и предложениям, касающихся работы сайта, можно написать на почтовый адрес')} <script type="text/javascript">eval(unescape('%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%61%20%68%72%65%66%3d%22%6d%61%69%6c%74%6f%3a%69%6e%66%6f%40%74%72%61%63%65%79%6f%75%72%73%65%6c%66%2e%63%6f%6d%22%3e%69%6e%66%6f%40%74%72%61%63%65%79%6f%75%72%73%65%6c%66%2e%63%6f%6d%3c%2f%61%3e%27%29%3b'))</script> ${_(u'или заполнив следующую форму:')}</p>

% if messageSent is True:
 <p class="warnings">${_(u'Сообщение успешно отправлено.')}</p>
% endif

<form name="contactForm" id="contactForm" action="${action_url}" method="post">
 <table>
  ${form.as_table()}
 </table>
 <p><input type="submit" name="submit" value="${_(u'Отправить')}" title="${_(u'Это нужно нажать, чтобы письмо отправилось.')}"/></p>
 <p>${_(u'Звёздочкой (<span class="required">*</span>) отмечены поля, обязательные для заполнения')}</p>
</form>
</%block>
