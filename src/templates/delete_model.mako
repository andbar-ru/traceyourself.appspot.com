<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Очистить какую-нибудь модель</title>
 </head>
 
 <body>
  
  <form action="/delete_data/model" method="post">
   % if cleared:
    <p>Модель ${cleared} очищена</p>
   % endif
   <p>Выберите модель, которую надо очистить.</p>
   <select name="model">
    <option selected="selected">Выберите модель</option>
    % for model in models:
    <option>${model}</option>
    % endfor
   </select>
   <input type="submit" value="Очистить" name="submit" onclick="return confirm('Ты реально хочешь очистить эту модель?')"/>
  </form>
  
 </body>
 
</html>
