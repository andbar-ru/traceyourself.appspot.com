<div id="header">
 <div id="logo">
  <img src="/img/logo.png" width="204" height="43" alt="Логотип" />
 </div>
 <div id="langs" class="toggle">
  <div class="switch">
   % if lang == 'en':
    <span class="left_position on">eng</span>
    <a class="right_position" href="${route}?lang=ru">рус</a>
   % else:
    <a class="left_position" href="${route}?lang=en">eng</a>
    <span class="right_position on">рус</span>
   % endif 
  </div>
 </div>
 <div id="animation_toggle" class="toggle">
  <p>${_(u'Анимация')}</p>
  <div class="switch">
   <span id="animationOn" class="left_position${' on' if animation is True else ' off'}">${_(u'Вкл')}</span>
   <span id="animationOff" class="right_position${' on' if animation is False else ' off'}">${_(u'Выкл')}</span>
  </div>
 </div>
 <!-- <div id="langs">
   <a href="${route}?lang=en"><img src="${_('/img/eng.png')}" alt="english" /></a>
   <a href="${route}?lang=ru"><img src="${_('/img/rus_active.png')}" alt="russian" /></a>
 </div> -->
 <div id="login"><%include file="login.mako"/></div>
</div>
