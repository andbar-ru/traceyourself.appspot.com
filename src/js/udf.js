/*
 * Здесь определяются сокращения часто используемых длинных функций
 */

$I = document.getElementById.bind(document);
$C = document.getElementsByClassName.bind(document);
$Q = document.querySelector.bind(document);
$QA = document.querySelectorAll.bind(document);
$E = document.createElement.bind(document);
$TN = document.createTextNode.bind(document);

if (typeof(Jed) !== 'undefined') {
  var jed = new Jed({
    'domain': 'messages',
    'locale_data': {
      'messages': i18n
    }
  });
}

function _(msg) {
  return jed.translate(msg).fetch();
} 

