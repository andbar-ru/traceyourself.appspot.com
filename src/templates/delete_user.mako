<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Удалить профиль какого-нибудь пользователя</title>
 </head>
 
 <body>
  
  <form action="/delete_data/user" method="post">
   % if cleared:
    <p>Профиль пользователя ${cleared} удалён</p>
   % endif
   <p>Выберите пользователя, профиль которого следует удалить вместе с данными</p>
   <select name="user">
    <option selected="selected">Выберите пользователя</option>
    % for user in users:
    <option>${user.key().name()}</option>
    % endfor
   </select>
   <input type="submit" value="Удалить" name="submit" onclick="return confirm('Ты действительно хочешь удалить профиль этого пользователя со всеми данными?')"/>
  </form>
  
 </body>
 
</html>
