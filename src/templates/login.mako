## email пользователя и ссылка для выхода.
<p>
 ${user.email() if user else ''}<br/>
 <a href="${logout_url}">${_(u'Выход') if user else _(u'Вход')}</a>
</p>
