// Скрипт запускается на всех страницах сайта

//$(document).ready(function() {{{1
$(document).ready(function() {
  var animationOn = $('#animationOn');
  var animationOff = $('#animationOff');
  animationOff.click(function() {
    if ($(this).hasClass('on')) {return false};
    var animationFrame = $('#animationFrame');
    $('#animationFrame').remove();
    animationOff.removeClass('off').addClass('on');
    animationOn.removeClass('on').addClass('off');
    var date = new Date(new Date().getTime() + 30*24*60*60*1000);
    document.cookie = "animation=false; path=/; expires="+date.toUTCString();
  })
  animationOn.click(function() {
    if ($(this).hasClass('on')) {return false};
    var animationFrame = $('#animationFrame');
    $('#header').prepend('<iframe id="animationFrame" src="/animation?lang=' + lang + '" width="1024" height="377" frameborder="0" name="MotionComposer" scrolling"0"><p>Your browser does not support iframes.</p></iframe>');
    animationOn.removeClass('off').addClass('on');
    animationOff.removeClass('on').addClass('off');
    var date = new Date(new Date().getTime() + 30*24*60*60*1000);
    document.cookie = "animation=true; path=/; expires="+date.toUTCString();
  })
});
