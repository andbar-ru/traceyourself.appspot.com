function initAnalysis() { //{{{1
  var H = '<div id="analysis" class="hidden">';

  H += '<div id="buttons">';
    H += '<button id="toggleChart" type="button" name="toggleChart">' + _('Показать график') + '</button>';
    H += '<button type="button" name="toggleStattable" id="toggleStattable">' + _('Показать статистические показатели') + '</button>';
    H += '<button type="button" name="toggleCorrtable" id="toggleCorrtable">' + _('Показать корреляционную таблицу') + '</button>';
    H += '<button type="button" name="toggleDatatable" id="toggleDatatable">' + _('Показать таблицу с данными') + '</button>';
  H += '</div>'

  H += '<div id="chartWrapper" class="tableWrapper hidden">';
    H += '<div><button class="propsSelect">' + _('Выбрать параметры для построения графика') + '</button></div>';
    H += '<div id="props4charts" class="propsDiv hidden"></div>';
    H += '<div id="chartContainer"></div>';
  H += '</div>';

  H += '<div id="stattableWrapper" class="tableWrapper hidden">';
    H += '<div>';
      H += '<button class="propsSelect">' + _('Выбрать параметры для отображения в таблице') + '</button>';
      H += '<button class="tablePopup">' + _('Показать таблицу в отдельном окне') + '</button>';
      H += '<button id="stattable2csv">' + _('Скачать таблицу в формате CSV') + '</button>';
      H += '<button id="stattable2xlsx">' + _('Скачать таблицу в формате XLSX') + '</button>';
    H += '</div>';
    H += '<div id="props4statTable" class="propsDiv hidden"></div>';
    H += '<div class="tableContainer" id="stattableContainer"></div>';
  H += '</div>';

  H += '<div id="corrtableWrapper" class="tableWrapper hidden">';
    H += '<div>';
      H += '<button class="propsSelect">' + _('Выбрать параметры для отображения в таблице') + '</button>';
      H += '<button class="tablePopup">' + _('Показать таблицу в отдельном окне') + '</button>';
      H += '<button id="corrtable2csv">' + _('Скачать таблицу в формате CSV') + '</button>';
      H += '<button id="corrtable2xlsx">' + _('Скачать таблицу в формате XLSX') + '</button>';
    H += '</div>';
    H += '<div id="props4corrTable" class="propsDiv hidden"></div>';
    H += '<div class="tableContainer" id="corrtableContainer"></div>';
  H += '</div>';

  H += '<div id="datatableWrapper" class="tableWrapper hidden">';
    H += '<div>';
      H += '<button class="propsSelect">' + _('Выбрать параметры и даты для отображения в таблице') + '</button>';
      H += '<button class="tablePopup">' + _('Показать таблицу в отдельном окне') + '</button>';
      H += '<button id="pagerToggle">' + _('Отключить разбиение на страницы') + '</button>';
      H += '<button id="datatable2csv">' + _('Скачать таблицу в формате CSV') + '</button>';
      H += '<button id="datatable2xlsx">' + _('Скачать таблицу в формате XLSX') + '</button>';
    H += '</div>';
    H += '<div id="props4dataTable" class="propsDiv hidden"></div>';
    H += '<div class="tableContainer" id="datatableContainer"></div>';
  H += '</div>';

  H += '<div id="table2file" class="hidden"></div>';

  H += '</div>';

  $I('analysisWrapper').innerHTML = H;
}

//}}}
$(document).ready(function() {
  // Скрытие/показ главной формы {{{1
  $('#mainFormToggle').toggle(function() {
    $('#mainFormWrapper').slideUp(200);
    $(this).html(_('Показать форму')).css({
      'border-bottom': '3px outset #cccccc',
      'border-radius': '5px'
    });
  }, function() {
    $('#mainFormWrapper').slideDown(200);
    $(this).html(_('Скрыть форму')).css({
      'border-bottom': '1px solid #e6e6e6',
      'border-radius': '5px 5px 0 0'
    });
  });
  //}}}
  // Отметить/Снять отметку со всех {{{1
  $('[name="selectAll4mainForm"]').click(function() {
    $(this).parent().find('input[type="checkbox"]').prop("checked", true);
    if (this.id === 'weatherSelectAll') {
      $('#residenceWrapper').addClass('required');
    }
  });
  $('[name="deselectAll4mainForm"]').click(function() {
    $(this).parent().find('input[type="checkbox"]').prop("checked", false);
    if (this.id === 'weatherDeselectAll') {
      $('#residenceWrapper').removeClass('required');
    }
  });
  //}}}
  // При выделении чего-нибудь из данных погоды помечать поле "Населённый пункт" как обязательное {{{1
  $('#weatherProps input[type="checkbox"]').change(function() {
    var weatherCheckboxes = $QA('#weatherProps input[type="checkbox"]')
    var residenceIsRequired = false;
    for (var i=0; i<weatherCheckboxes.length; i++) {
      if (weatherCheckboxes[i].checked === true) {
        residenceIsRequired = true;
        break;
      }
    }
    if (residenceIsRequired) {
      $('#residenceWrapper').addClass('required');
    }
    else {
      $('#residenceWrapper').removeClass('required');
    }
  });
  //}}}
  // Проверка формы при отправке, отправка и приём данных {{{1
  $('#commonDataForm').submit(function(event) {
    var errors = false;
    // Проверка дат
    var dateFrom = this.dateFrom.value;
    var dateTo = this.dateTo.value;
    var dateFromError = $I('dateFromError');
    var dateToError = $I('dateToError');
    var residenceError = $I('residenceError');
    var commonPropertiesError = $I('commonPropertiesError');
    var formErrors = $I('formErrors');
    dateFromError.innerHTML = '';
    dateToError.innerHTML = '';
    residenceError.innerHTML = '';
    commonPropertiesError.innerHTML = '';
    formErrors.innerHTML = '';

    if (!dateFrom) {
      dateFromError.innerHTML = _('Вы не указали дату "с"!');
      errors = true;
    }
    else if (!/^\d{4}-\d{2}-\d{2}$/.test(dateFrom)) {
      dateFromError.innerHTML = _('Неправильная дата "с"! Формат даты должен быть "гггг-мм-дд".');
      errors = true;
    }
    if (!this.dateTo.value) {
      dateToError.innerHTML = _('Вы не указали дату "по"!');
      errors = true;
    }
    else if (!/^\d{4}-\d{2}-\d{2}$/.test(dateTo)) {
      dateToError.innerHTML = _('Неправильная дата "по"! Формат даты должен быть "гггг-мм-дд".');
      errors = true;
    }
    if (!errors) {
      var dateFrom = new Date(dateFrom);
      var dateTo = new Date(dateTo);
      if (dateFrom == 'Invalid Date') {
        dateFromError.innerHTML = _('Неправильная дата "с"! Не существует.');
        errors = true;
      }
      if (dateTo == 'Invalid Date') {
        dateToError.innerHTML = _('Неправильная дата "по"! Не существует.');
        errors = true;
      }
    }
    if (!errors) {
      if (dateFrom > dateTo) {
        dateFromError.innerHTML = _('Дата "с" не может быть позднее даты "по"!');
        errors = true;
      }
    }
    // Проверка населённого пункта при выборе данных погоды
    if ($I('residenceWrapper').classList.contains('required')) {
      if (this.residence.value == '__None') {
        residenceError.innerHTML = _('Если вы выбрали данные погоды, то следует выбрать и населённый пункт.');
        errors = true;
      }
    }
    // Проверка выбора хотя бы одного показателя
    var checkboxes = $QA('#commonProperties input[type="checkbox"]');
    var checked = false;
    for (var i=0; i<checkboxes.length; i++) {
      if (checkboxes[i].checked === true) {
        checked = true;
        break;
      }
    }
    if (checked === false) {
      commonPropertiesError.innerHTML = _('Для проведения анализа нужно выбрать хотя бы один показатель.')
      errors = true;
    }
    // Если нет ошибок, запрашиваем данные по ajax.
    if (!errors) {
      formErrors.innerHTML = _('Подождите, загружаются данные...');
      $.getJSON('/get_common_data', $(this).serializeArray())
        .done(function(data) {
          if (data.errors) {
            var html = _('При проверке формы произошли ошибки:') + '<br/>';
            for (var i=0; i<data.errors.length; i++) {
              html += '* ' + data.errors[i] + '<br/>';
            }
            formErrors.innerHTML = html;
          }
          else {
            formErrors.innerHTML = '';
            DATA = data; // Глобальная переменная
            initAnalysis();
            doAnalysis();
            $I('analysis').classList.remove('hidden');
            $('#mainFormToggle').click();
          }
        })
        .fail(function() {
          console.log("FAILFAIL");
          formErrors.innerHTML = _('ОШИБКА! Не удалось загрузить данные.');
        });
    }
    event.preventDefault();
  });
  //}}}
});
