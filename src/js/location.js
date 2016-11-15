// Подгрузка географических названий посредством ajax
function location_error_msg(type) { //{{{1
  var typeMsg = {
    'country': _('Вы не выбрали страну!'),
    'region': _('Вы не выбрали регион!'),
    'district': _('Вы не выбрали район!')
  };
  var msg = typeMsg[type];
  var selector = 'label[for="' + type + '"]';
  var id = type + 'Error';
  var html = '<span style="margin-left:10px;" id="' + id + '" class="error">' + msg + '</span>';
  $(selector).after(html);
}
//}}}
function init_location_code() { //{{{1
  $I('get_regions').onclick = function() { //{{{2
    var td = $(this.parentNode);

    $('#countryError').remove();
    var country = $I('country');
    var cValue = country.value;
    if (!cValue) {
      location_error_msg('country');
      return false;
    }
    country.setAttribute('data-initial', cValue);

    var data = {
      lang: $I('lang').value,
      country: cValue
    };
    $.get('/get_regions', data, function(html) {
      td.nextAll().remove();
      td.after(html);
    });
    return false;
  }
  //}}}
  $('#get_districts').live('click', function() { //{{{2
    var td = $(this.parentNode);

    $('#countryError').remove();
    var country = $I('country');
    var cValue = country.value;
    var cInit = country.getAttribute('data-initial');
    if (!cValue) {
      location_error_msg('country');
      return false;
    }
    if (cValue !== cInit) {
      cValue = cInit;
      country.value = cValue;
    }

    $('#regionError').remove();
    var region = $I('region');
    var rValue = region.value;
    if (!rValue) {
      location_error_msg('region');
      return false;
    }
    region.setAttribute('data-initial', rValue);

    var data = {
      lang: $I('lang').value,
      country: cValue,
      region: rValue
    };
    $.get('/get_districts', data, function(html) {
      td.nextAll().remove();
      td.after(html);
    });
    return false;
  });
  //}}}
  $('#get_localities').live('click', function() { //{{{2
    var td = $(this.parentNode);

    $('#countryError').remove();
    var country = $I('country');
    var cValue = country.value;
    var cInit = country.getAttribute('data-initial');
    if (!cValue) {
      location_error_msg('country');
      return false;
    }
    if (cValue !== cInit) {
      cValue = cInit;
      country.value = cValue;
    }

    $('#regionError').remove();
    var region = $I('region');
    var rValue = region.value;
    var rInit = region.getAttribute('data-initial');
    if (!rValue) {
      location_error_msg('region');
      return false;
    }
    if (rValue !== rInit) {
      rValue = rInit;
      region.value = rValue;
    }

    $('#districtError').remove();
    var dValue = $I('district').value;
    if (!dValue) {
      location_error_msg('district');
      return false;
    }

    var data = {
      lang: $I('lang').value,
      country: cValue,
      region: rValue,
      district: dValue 
    };
    $.get('/get_localities', data, function(html) {
      td.nextAll().remove();
      td.after(html);
    });
    return false;
  });
  //}}}
}
//}}}
