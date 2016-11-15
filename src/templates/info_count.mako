<html>

<head>
 <meta charset="utf-8"/>
 <title>Show count</title>
 <link rel="stylesheet" href="/css/dateinput.css"/>
</head>
 
 <body>
  
  <form action="/info/count" method="post">
   % if model_info:
    <p>Количество объектов в модели ${model_info[0]} = ${model_info[1]}</p>
   % endif
   <p>Выберите модель, количество объектов в которой нужно узнать.</p>
   <select name="model">
    <option selected="selected">Выберите модель</option>
    % for model in models:
    <option>${model}</option>
    % endfor
   </select>
   <input type="submit" value="Посчитать" name="submit" />
  </form>
  
 </body>
 
</html>
