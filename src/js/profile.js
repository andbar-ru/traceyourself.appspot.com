// $(document).ready(function() {{{1
$(document).ready(function() {
  // Скрытие полей "Единица измерения" и "Свойства шкалы" {{{2
	// Скры(ва)ть поле "Единица измерения", если тип нечисловой
	// Скры(ва)ть поля "Свойства шкалы", если тип не 'Шкала'
	var numeric_types = ['int', 'float'];
	$('div.details').each(function(i,div) {
		var type = $('#type', div).val();
		if (numeric_types.indexOf(type) == -1) {
			$('#measure_field', div).hide();
		};
		if (type != 'scale') {
			$('#scale_attrs_field', div).hide();
		};

		$('#type', this).change(function() {
			if (numeric_types.indexOf(this.value) != -1) {
				$('#measure_field', div).show();
			}
			else {
				$('#measure_field', div).hide();
			};
			if (this.value == 'scale') {
				$('#scale_attrs_field', div).show();
			}
			else {
				$('#scale_attrs_field', div).hide();
			}
		});
	});

	// Показать/Скрыть данные профиля {{{2
	$('#toggle_static_data').toggle(function() {
		$('#static_data').show();
		$(this).val(_('Утаить'));
	}, function() {
		$('#static_data').hide();
		$(this).val(_('Явить'));
	});

	// Редактировать личные данные {{{2
	$('#toggleEditStatic').toggle(function() {
	  $(this).html(_('Скрыть форму')).parent().next().slideDown();
	}, function() {
	  $(this).html(_('Редактировать личные данные')).parent().next().slideUp();
	});

	// Показать/Скрыть общие параметры {{{2
	$('#toggle_common_props').toggle(function() {
		$('#common_props_div').show();
		$(this).val(_('Утаить'));
	}, function() {
		$('#common_props_div').hide();
		$(this).val(_('Явить'));
	});

	// Показать/Скрыть подробности {{{2
	// По нажатию кнопки
	$('button[name="toggle_fold"]').toggle(function() {
		$(this).siblings('div.details:first').slideDown();
		$(this).attr({'class':'fold', 'title':_('Свернуть')});
	}, function() {
		$(this).siblings('div.details:first').slideUp();
		$(this).attr({'class':'unfold', 'title':_('Развернуть')});
	});
	// По клику по панели/имени параметра/элемента
	$('div.info').click(function() {
		$(this).prev().click();
	});

	// Добавить параметр {{{2
  $('button[name="add_prop"]').toggle(function() {
    $(this).html(_('Скрыть форму')).parent().next().slideDown();
  }, function() {
    $(this).html(_('Добавить параметр')).parent().next().slideUp();
  }); 

  // Якоря на формы {{{2
	// Редактирование личных данных
	if ($Q('a[name="edit_static"]')) {
    var btn = $I('toggle_static_data'); // null в процессе создания профиля
    if (btn) {
	    btn.click();
	    $I('toggleEditStatic').click();
	  }
	  document.location.href = '#edit_static';
	}
  // Добавление параметра
	if ($Q('a[name="add_prop"]')) {
	  $Q('button[name="add_prop"]').click();
	  document.location.href = '#add_prop';
	}
	// Редактирование параметра
	var anchor = $Q('a[name="edit_prop"]');
	if (anchor) {
	  $(anchor).parent().prev().click();
	  document.location.href = '#edit_prop';
	}
  //}}}
  init_location_code(); //from location.js
}); // endof $(document).ready
