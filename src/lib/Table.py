#coding: utf-8

"""
Модуль предоставляет классы, предназначенные для хранения, оперирования и
представления табличных структур.
Навеяно проектом Филиппа Лагадека HTML.py website: http://www.decalage.info/python/html
"""

def attrs2str(attrs):
	"""Принимает словарь аргументов и возвращает строку аргументов типа
	'border="1", cellpadding="1", cellspacing="1", class="tablesorter"'
	"""
	if attrs:
		return " " + " ".join(['%s="%s"'%(k,v) for k,v in attrs.iteritems()])
	else:
		return ""

class TableCell(object):
	"""Предназначен для хранения информации об одной ячейке, даже несуществующей."""
	def __init__(self, text="&nbsp;", th=False, attrs={}):
		"""Инициализирует объект ячейки таблицы.
		Аргументы:
		text  - содержимое ячейки, по умолчанию неразрывный пробел;
		th    - Отрисовывать с помощью тега th;
		attrs - атрибуты, выводимые непосредственно в теге <td>/<th>,
		"""
		self.text = text
		self.th = th
		self.attrs = attrs

	def __unicode__(self):
		"""Возвращает HTML-код ячейки таблицы в виде юникод-строки"""
		if not self.th:
			return "   <td%s>%s</td>\n" %  (attrs2str(self.attrs), self.text)
		else:
			return "   <th%s>%s</th>\n" %  (attrs2str(self.attrs), self.text)


class TableRow(object):
	"""Предназначен для хранения одной строки таблицы."""
	def __init__(self, cells=[], th=False, attrs={}):
		"""Инициализирует объект строки таблицы
		Аргументы:
		cells - ячейки. Д.б. экземплярами класса TableCell
		th    - при выводе html применять теги <th> вместо <td>.
		attrs - атрибуты, выводимые непосредственно в теге <tr>,
		"""
		self.th = th
		self.attrs = attrs
		self.cells = []
		for cell in cells:
			self.add_cell(cell)
	

	def __getitem__(self, index):
		return self.cells[index]

	def __setitem__(self, index, value):
		if isinstance(value, TableCell):
			self.cells[index] = value
		else:
			self.cells[index].text = unicode(value)

	def add_cell(self, cell="&nbsp;", th=None, attrs={}):
		"""Добавляет объект ячейки к self.cells. Объект ячейки д.б. экземпляром класса TableCell.
		Аргументы:
		cell  - ячейка, которую надо добавить к строке. Если не является экземпляром класса
		        TableCell, то необходимо преобразовать
		th    - Отрисовывать с помощью тега th.
				Учитывается, если cell не является экземпляром класса TableCell.
		attrs - атрибуты, выводимые непосредственно в теге <td>/<th>,
				Учитывается, если cell не является экземпляром класса TableCell.
		"""
		if th == None:
			th = self.th
		if not isinstance(cell, TableCell):
			# Создаём объект TableCell
			# считаем, что в первом аргументе передаётся либо строка, либо число
			text = unicode(cell)
			cell = TableCell(text, th, attrs)
		self.cells.append(cell)


	def __unicode__(self):
		"""Возвращает HTML-код строки таблицы в виде юникод-строки"""
		# открываем строку
		result = "  <tr%s>\n" % attrs2str(self.attrs)
		# добавляем ячейки
		for cell in self.cells:
			result += unicode(cell)
		# закрываем строку
		result += "  </tr>\n"

		return result


class Table(object):
	"""Класс, предназначенный для хранения и представления табличных данных.
	Должен позволять легко и эффективно получать данные как построчно (для создания html-таблиц),
	так и постолбно (для создания JSON-форматированной строки).
	Должен учитывать существование таких структур, как thead, tbody и tfoot.
	Должен оперировать параметрами rowspan и colspan, а также другими атрибутами,
	которые присущи html-таблицам и её строкам и ячейкам.

	Информация хранится в атрибуте self.rows, являющейся по сути списком,
	элементами которой служат экземпляры класса TableRow.
	Для удобного получения столбцов, объекты TableRow должны содержать одинаковое количество ячеек.
	Несущесвующие ячейки при наличии rowspan, colspan д.б. представлены объектами TableCell
	с пустым контентом."""

	def __init__(self, thead_rows=[], rows=[], tfoot_rows=[], caption="", attrs={}):
		"""Инициализирует объект таблицы.
		К.п., она создаётся пустой и заполняется с помощью метода add_row.
		Аргументы:
		thead_rows - строки, определяемые внутри тега <thead>. Д.б. экземплярами TableRow
		rows - обычные строки. Определяются внутри тега <tbody>. Д.б. экземплярами TableRow
		tfoot_rows - строки, определяемые внутри тега <tfoot>. Д.б. экземплярами TableRow
		attrs - атрибуты, выводимые непосредственно в теге <table>.
		"""
		self.caption = caption
		self.attrs = attrs
		self.thead_rows = []
		for row in thead_rows:
			self.add_row(row, group="thead")
		self.tfoot_rows = []
		for row in tfoot_rows:
			self.add_row(row, group="tfoot")
		self.rows = []
		for row in rows:
			self.add_row(row)


	def add_row(self, row=None, group="tbody", th=None, attrs={}):
		"""Добавляет объект строки к self.rows. Объект строки д.б. экземпляром класса TableRow.
		Аргументы:
		row   - строка, которую надо добавить к таблице. Если не является экземпляром класса
		        TableRow, то перед добавлением необходимо к нему преобразовать.
		group - группа, к которой относится строка (thead, tbody, tfoot). Строки, относящиеся к
		        группам thead и tfoot, при выводе html определяеются перед обычными строками.
		th    - при выводе html применять теги <th> вместо <td>.
				Учитывается, если row не является экземпляром класса TableRow.
		attrs - атрибуты, выводимые непосредственно в теге <tr>,
				Учитывается, если row не является экземпляром класса TableRow.
		"""
		if not isinstance(row, TableRow):
			# создаём объект TableRow
			# Если row какой-либо итерируемый объект, но не строка,
			# то каждый элемент рассматривается как ячейка.
			if th == None:
				if group in ["thead", "tfoot"]:
					th = True
				else:
					th = False
			if hasattr(row, "__iter__"):
				row = TableRow(cells=row, th=th, attrs=attrs)
			else:
				# неправильный тип -> пустая строка
				row = TableRow(cells=[], th=th, attrs=attrs)
		# помещаем объект строки в соответствующую группу
		if group == 'thead':
			self.thead_rows.append(row)
		elif group == 'tfoot':
			self.tfoot_rows.append(row)
		else:
			self.rows.append(row)


	def __unicode__(self):
		"""Возвращает HTML-код таблицы в виде юникод-строки"""
		# открываем таблицу
		result = "<table%s>\n" % attrs2str(self.attrs)
		# Добавляем заголовок, если есть
		if self.caption:
			result += '<caption>%s</caption>\n' % self.caption
		# Сначала добавляем заголовочные строки, если они есть
		if self.thead_rows:
			result += " <thead>\n"
			for row in self.thead_rows:
				result += unicode(row)
			result += " </thead>\n"
		# Затем добавляем подвал таблицы
		if self.tfoot_rows:
			result += " <tfoot>\n"
			for row in self.tfoot_rows:
				result += unicode(row)
			result += " </tfoot>\n"
		# Затем добавляем тело таблицы
		result += " <tbody>\n"
		for row in self.rows:
			result += unicode(row)
		result += " </tbody>\n"
		# Закрываем таблицу
		result += '</table>'

		return result
