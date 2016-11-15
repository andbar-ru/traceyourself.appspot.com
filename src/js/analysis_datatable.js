function pagerToggle() {
  $I('pagerToggle').onclick = function() {
    var mode = /Отключить|Disable/.test(this.innerHTML);
    $('#dataTable').trigger((mode ? 'disable' : 'enable') + '.pager');
    this.innerHTML = (mode ? _('Включить') : _('Отключить')) + _(' разбиение на страницы');
    return false;
  };
}

function datatableSort() {
  $('#dataTable').tablesorter({
    cancelSelection: false,
    emptyTo:'bottom',
    dateFormat: 'ddmmyyyy',
    selectorHeaders: '> thead th',
    sortReset: true
  }).bind('pagerChange pagerInitialized', function() {
    // Пэйджер автоматически включается при сортировке таблицы
    $('#pagerToggle').text(_('Отключить разбиение на страницы'));
  }).tablesorterPager({
    container: $('div.pager'),
    output: _('показаны строки с {startRow} по {endRow} из {totalRows}'),
    updateArrows: true,
    size: 20
  });
}
