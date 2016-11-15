## Inherit {{{1
<%inherit file="base.mako"/>

## Block Title {{{1
<%block name="Title">${_(u'Анализ данных')}</%block>

## Block Content {{{1
<%block name="Content">
<p><a href="/analysis_saved">${_(u'Анализировать сохранённые данные')}</a></p>
<p><a href="/analysis_test">${_(u'Анализировать тестовые данные')}</a></p>
</%block>
