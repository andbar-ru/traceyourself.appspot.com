<html>

<head>
 <meta charset="utf-8"/>
 <title>Serialize model</title>
</head>
 
<body>
 
<form action="/download_data" method="post">
 <p>Выберите модель, которую надо сериализовать.</p>
 <p>
  <input type="radio" name="how" value="all" /> Все объекты
  <select name="model">
   <option selected="selected">Выберите модель</option>
   % for model in models:
   <option>${model}</option>
   % endfor
  </select>
 </p>
 <p>
  <input type="radio" name="how" value="query" /> По запросу (GlqQuery)<br/>
  SELECT * FROM <input type="text" name="qModel" size="20" value="model"/>
  <input type="text" name="condition" size="100" value="condition"/>
 </p>
 <input type="submit" value="Выполнить" name="submit" />
</form>
 
</body>
 
</html>
