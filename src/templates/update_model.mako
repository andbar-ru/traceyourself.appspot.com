<!DOCTYPE html>
<html>
 <head>
  <meta charset=utf-8" />
  <title>Обновить какую-нибудь модель</title>
 </head>

 <body>
  <form action="/update_model" method="post">
   <p><b>Эту сценарий лучше запускать как backend.</b></p>
   <p>Выберите модель, которую следует обновить, чтобы заработали или, наоборот, перестали работать индексы.</p>
   <p><label>Модель:&nbsp;<input id="model" type="text" name="model" /></label></p>
   <input type="submit" value="Обновить" name="submit" onclick="return confirm('Подтвердить')"/>
  </form>

 </body>

</html>
