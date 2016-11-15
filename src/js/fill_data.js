// локализация календаря {{{1
$.tools.dateinput.localize("ru", {
  months: 'январь,февраль,март,апрель,май,июнь,июль,август,сентябрь,октябрь,ноябрь,декабрь',
  shortMonths: 'янв,фев,мар,апр,май,июн,июл,авг,сен,окт,ноя,дек',
  days: 'воскресенье,понедельник,вторник,среда,четверг,пятница,суббота',
  shortDays: 'вс,пн,вт,ср,чт,пт,сб'
});
var ruFormat = /(\d{2})\.(\d{2})\.(\d{4})/;
var enFormat = /(\d{2})\/(\d{2})\/(\d{4})/;

//function DatesIsEqual(date1, date2) {{{1
function DatesIsEqual(date1, date2) {
  // Формат может быть "гггг-мм-дд" и "дд.мм.гггг", приводим к одному формату
  var date1 = date1.replace(ruFormat, "$3-$2-$1").replace(enFormat, "$3-$2-$1");
  var date2 = date2.replace(ruFormat, "$3-$2-$1").replace(enFormat, "$3-$2-$1");
  return date1 == date2;
}

$(document).ready(function() { //{{{1
  // DateInput {{{2
  // global variables
  var dateInput = document.getElementById("date");
  var supportsOninput = false; // Поддерживает ли браузер событие oninput

  // По-умолчанию сегодня. Если в браузере правильная дата, то ставим его (оно может отличаться от UTC на ±сутки)
  if (document.getElementById("isToday").value == "True") {
    var clientDate = new Date();
    var UTCToday = new Date(document.getElementById("UTCdate").value);
    var oneDay = 1000*60*60*24;
    var dateDiff = Math.abs(parseInt((clientDate-UTCToday)/oneDay));
    if (dateDiff <= 1) {
      var clientDateString = clientDate.isoDate();
      if (clientDateString != UTCToday) {
        dateInput.value = clientDateString;
        dateInput.setAttribute("max", clientDateString);
      }
    }
  }

  // Если дата в русском формате, преобразовываем в iso-формат (иначе dateinput ставит текущую дату)
  dateInput.value = dateInput.value.replace(ruFormat, "$3-$2-$1").replace(enFormat, "$3-$2-$1");
  var currentDate = dateInput.value; // чтобы грузить данные только при изменении даты
  //}}}
  function UpdateData() { //{{{2
    if (!DatesIsEqual(this.value, currentDate)) {
      $('#update_data').click();
    }
  }
  //}}}
	// Изменить место пребывания {{{2
	$('#toggleLocationForm').toggle(function() {
	  $(this).html(_('Скрыть форму')).parent().next().slideDown();
	}, function() {
	  $(this).html(_('Изменить')).parent().next().slideUp();
	});
	$I('resetLocationForm').onclick = function() {
	  $('#get_regions').parent().nextAll().remove();
	  $I('toggleLocationForm').click();
	  return false;
	}
	//}}}
	// Редактирование locationForm {{{2
	if ($Q('a[name="locationForm"]')) {
	  $I('toggleLocationForm').click();
	  document.location.href = '#locationForm';
	}
	//}}}
  // Скрыть кнопку "Обновить значения параметров"
  $("#update_data").hide();
  // Скрыть подсказку по формату дат
  $("#dates_hint").hide();
  // Поле выбора даты
  if (navigator.userAgent.toLowerCase().indexOf('firefox') !== -1) {
    var selectors = false; //не работает выбор в firefox>=20(17.0.1esr) (https://github.com/jquerytools/jquerytools/issues/982)
  }
  else {
    var selectors = true;
  };

  if (lang === 'en') {
    var format = 'dd/mm/yyyy';
  }
  else {
    var format = 'dd.mm.yyyy';
  }
  $(dateInput).dateinput({
    lang: lang,
    format: format,
    selectors: selectors,
    firstDay: 1
  }).parent().removeAttr('title'); 
  // При изменении даты перезагружать страницу
  $('#date').change(UpdateData);

  init_location_code(); //from location.js
});
