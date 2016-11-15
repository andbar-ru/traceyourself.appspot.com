<!DOCTYPE html>
<html>
 <head>
  <meta charset=utf-8" />
  <title>Удалить какое-нибудь свойство из всех объектов модели</title>
 </head>

 <body>
  <form action="/delete_data/model_attr" method="post">
   <p>Выберите модель и свойство, которое надо удалить из модели.</p>
   <p><label>Модель:&nbsp;<input id="model" type="text" name="model" /></label></p>
   <p><label>Свойство:&nbsp;<input id="attr" type="text" name="attr" /></label></p>
   <input type="submit" value="Удалить" name="submit" onclick="return confirm('Ты реально хочешь удалить свойство `' + document.getElementById('attr').value + '` из модели `' + document.getElementById('model').value + '`?')"/>
  </form>

 </body>

</html>
