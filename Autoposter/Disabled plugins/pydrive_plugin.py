"""
Название: Плагин работы с гугл диском/pydrive.py
Тип: Плагин работы с гугл.диском
Статус: Не готов
Краткое описание: Плагин для гугл.диска. В файде "dancing with a tambourine.txt" ("танцы с бубном") объяснено как включить google drive
"""
import asyncio # Импортируем асинхронность

from aiofiles import open as _open # Импортируем асинхронную работу с файлом
from pydrive.auth import GoogleAuth # Импортируем аутентификацию
from pydrive.drive import GoogleDrive # Импортируем раюоту с гугл диском
from random import shuffle # Импортируем перемешивание списка

from logging_plugin import Async_logging # Импортируем асинхронное логгирование

googleauth = GoogleAuth() # Аутентификация
googleauth.LocalWebserverAuth() # Запускаем localhost:8080
drive = GoogleDrive(googleauth) # Создаём объект GoogleDrive

log = Async_logging() # Инициализация лога

class Google_files(): # Объявляем класс
	"""
ViewingWarning: Further viewing will lead to surprise (bad surprise) and a stroke of the programmer, we do not advise you to continue reading this spaghetti-code (shitcode)
	"""
	
	def __init__(self): # Функция инициализации
		self.files = 0 # Количество файлов
		self.names = [] # Имена
		self.drive_files = [] # Объекты файлов
		asyncio.run(log.set_file_name("pydrive_plugin.log")) # Меняем название лога
		asyncio.run(log.begin()) # Стираем старый, начинаем новый лог
		asyncio.run(log.record("Создан объект гугл файлов")) 
	
	async def set_files(self, file): # Новый файл
		self.names.append(file) # Записываем в список
		self.files = len(names) # Записываем новое значение
		await log.record(f"Новый файл: {file}")
	
	async def upload_files(self): # Загрудаем файлы
		file_names = self.names # Получаем имена
		for file_name in file_names: # Проходимся циклом по именам
			try:
				async with _open(file_name, "r") as file: # Открываем новый файл
					all_lines = await file.read() # Читаем все линии
					await file.close()
				file_in_cloud = drive.CreateFile({"title": file_name}) # Создаём файл
				file_in_cloud.SetContentString(all_lines) # Меняем контент
				file_in_cloud.Upload() # Загружаем
				self.drive_files.append(file_name) # Сохраняем объект файла в облако
				await log.record(f"Файл {file_name} загружен в облако")
			except Exception as ex: # Обработка ошибок
				await log.record(f"Файл {file_name} не загружен в облако\nПричины: {ex}")
	
	async def get_file_in_cloud(self): # Получаем файл из облака
		"""
CriticalViewingWarning: We warned you
		"""
		try:
			file_in_cloud = [] # Файлы в облоке
			file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() # Поиск всех файлов не в корзине и не родители (???)
			for file in file_list: # Пробегаемся циклом
				file_in_cloud.append(file['id']) # Добавляем file_id в список
			
			shuffle(file_in_cloud) # Перемешиваем
			
			file = drive.CreateFile({"id": file_in_cloud[0]}) # Создаём файл с этим же ID (???)
		except Exception as ex: 
			return (0, ex)