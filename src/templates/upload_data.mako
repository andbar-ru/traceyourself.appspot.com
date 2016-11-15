<html>

<head>
 <meta charset="utf-8"/>
 <title>Deserialize model</title>
</head>
 
<body>
 
<form action="/upload_data" method="post">
 <p>Выберите файл, который надо десериализовать и записать в хранилище</p>
 <select name="file">
  <option selected="selected">Выберите файл</option>
  % for file in files:
  <option>${file}</option>
  % endfor
 </select>
 <input type="submit" value="Выполнить" name="submit" />
</form>
 
</body>
 
</html>
