"""
Название: Плагин асинхронного логгирования/logging_plugin.py
Тип: Плагин логгирования
Статус: Готов к использованию
Краткое описание: Плагин для логов.
Интересные факты:
- Не зависит от других плагинов. 
- Импортирует меньше всего
"""
from aiofiles import open as _open # Импортируем асинхронное открытий файлов
from os import remove # Импортируем удаление

class Async_logging(): # Обьявляем класс
	
	def __init__(self): # Инициализация
		self.name = "log_file.log" # Название файла (изменяемо)
		self.version = "1.0" # Версия (неизменяемо)
		self.hash = False # Хэшировать или нет (изменяемо)
		self.hashing = "" # Хэш (сам изменяется)
	
	async def set_file_name(self, name: str): # Изменение названия файла
		self.name = name
	
	async def set_hash(self, parameter: bool): # Изменяем параметр хэширования
		self.hash = parameter
	
	async def delete(self): # Ужалить файл с логом
		remove(self.name)
	
	async def remove_hash(self): # Удаляем хэш
		self.hash = ""
	
	async def begin(self): # Начало лога
			async with _open(self.name, "w", encoding = "utf-8") as log:
				await log.write("") # Стираем всё записываем ничего
				await log.close()
	
	async def record(self, record): # Запись
		if self.hash:
			self.hashing += f"{record} -- " # В хэш запись идёт такая
		else:
			async with _open(self.name, "a", encoding = "utf-8") as log: # Вне хэша запись такая
				await log.write(f"{record}\n")
				await log.close()
	
	async def error(self, error, msg=None): # Ошибка
		if self.hash: # Если хэшируется
			self.hashing += f"Error!\n{error}\nComment: {msg} -- "
		else:
			async with _open(self.name, "a", encoding = "utf-8") as log:
				await log.write(f"Error!\n{error}\nComment: {msg}") # Записываем
				await log.close()
	
	async def hash_and_remove(self, parameter: bool): # Хэшируем файл
		if parameter:
			self.hash = parameter
			async with _open(self.name, "r", encoding = "utf-8") as log_end:
				file = await log_end.readlines()
			for string_ in file: # Пробегаемся циклом по записи хэша
				await self.record(string_)
			await self.delete() # После записи в хэш ужаляем файл
	
	async def hash_in_file(self): # Записываем хэш
		async with _open(self.name, "w", encoding = "utf-8") as log:
			for hash_msg in self.hashing: # Пробегаемся по хэшу циклом
				await log.write(hash_msg)
			await log.close() # Закрываем файл