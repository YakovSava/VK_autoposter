"""
Название: Связующий плагин/binder_plugin.py
Тип: Связующий основной плагин
Статус: Готов к использованию
Краткое описание: Плагин для получения постов и фото
Интересные факты:
- Над этим плагином работа шла больше всего
- Binder - Связующее вещество (© Яндекс.переводчик)
"""
import asyncio # Импортируем асинхронность

from aiofiles import open as _open # Импортируем асинхронное открытие файла
from random import shuffle, choice # Импортируем перемешку списка
from os.path import join # Импортируем из работы с системой вхождение
from os import listdir # Импортируем самую полезную штуку на земле... тоесть список файлов в определённом каталоге
from time import time

from plugins.logging_plugin import Async_logging # Импортируем плагин асинхронного логгирования

log = Async_logging() # Инициализация логгирования

class Binder(): # Обьявляем класс
	
	def __init__(self): # Инициализируем
		self.return_object = {"code": None, # Это шаблон)
							"file": None, 
							"content": None}

		asyncio.run(log.set_file_name("binder_log.log")) # Меняем название файла
		asyncio.run(log.begin()) # Стираем старый, записываем новый файл
	
	async def get_raw_hashtags(self): # Получение хэштегов
		await log.record("Получаем хэштеги")
		try:
			re_obj = self.return_object # Шаблон, говорю же
			async with _open("hashtags.txt", "r", encoding="utf-8") as hashtags_file: # Открываем файл с хжштегами

				await log.record("Открытие файла")
				content = (await hashtags_file.read()).split() # Читаем, разделяем на слова

				shuffle(content) # Перемешиваем слова
				re_obj["content"] = content # Записываем в возвращаемый объект

				await hashtags_file.close() # Закрываем файл
			await log.record("Файл закрыт")

			re_obj["file"] = "hashtags.txt"
			re_obj["code"] = 1 # Записываем код

		except Exception as ex:
			re_obj["code"] = 0 # При какой либо ошибке код другой и не выполняем
			re_obj["content"] = ex # Записываем ошибку

		finally:
			await log.record("Возвращение хэштегов")
			return re_obj # В любом случае возвращаем объект
	
	async def poll(self, pool_counter = 0): # Пул
		parameters = await self.get_parameter()

		result = [] # Создаём список результатов
		media = [] # Создаём список медиа (Путей к ним и названий)

		data_type = ((".png", ".jpg", ".gif"), # Типы данных
					(".txt", ".log"), 
					".md",
					(".avi", ".mp4", ".3gp", ".mov", ".flv", ".wmv")) # .md вообще хз зачем добавил. Мой файловый менеджер вообще считает что .js тоже текстовый файл... Запускаю я через npm просто)
		await log.record("Запрос к биндеру...")
		try:
			folders_with_files = listdir('Datas')
			
			folders_with_files.sort()
			folders_with_files = folders_with_files[pool_counter]
			
			fwf = listdir('Datas')
			await self.save_folder_order_parameter(len(fwf))

			#print(fwf, ' --> ', folders_with_files)

			files = choice(listdir(f"Datas/{folders_with_files}")) # Переходим к ней в директорию
			finally_path = f"Datas/{folders_with_files}/{files}/"

			files_in_path = listdir(finally_path)

			for file_name in files_in_path: # Запускаем цикл
				await log.record(f"Получаем файл {file_name}")
				if ((file_name[-4:] in data_type[1]) or (file_name[-3:] in data_type[2])): # Проверяем данные: текст

					async with _open(join(finally_path, f"{file_name}"), "r", encoding="utf-8") as open_file:
						text = await open_file.read() # Читаем
						result.append(text) # Загружаем

						await open_file.close() # Закрываем

				elif (file_name[-4:] in data_type[0]): # Проверяем данные: фото
					media.append([finally_path, file_name]) # Слхраняем путь к файлу и файловое имя

				elif (file_name[-4:] in data_type[3]):
					media.append(["video", finally_path, file_name])

			result.append(media) # Закидываем фото в результаты
			return (1, result) # Возвращаемся их

		except Exception as ex:
			return (0, ex)
	
	async def get_donors(self): # Подучение доноров
		try:
			await log.record("Получение доноров...")
			async with _open("donors.txt", "r", encoding="utf-8") as file_with_donors: # Открытий файла с донорами
				all_donors = await file_with_donors.read() # Все доноры

				await file_with_donors.close() # Закрываем файл

			donors = all_donors.split() # Разделяем слова в список
			shuffle(donors)
			return (1, donors) # возвращаем
			
		except Exception as ex:
			return (0, ex)

	async def get_parameter(self):
		await log.record("Запрос параметров")
		async with _open(join('plugins/configs', 'config.json'), 'r', encoding='utf-8') as json_parameter_file:
			parameters_string = await json_parameter_file.read()
			await json_parameter_file.close()
		dictionary = eval(f'dict({parameters_string})')
		await log.record("Возвращение параметров")
		return dictionary

	async def save_folder_order_parameter(self, new:int):
		parameters = await self.get_parameter()
		parameters['folder_order_length'] = new
		async with _open(join('plugins/configs', 'config.json'), 'w', encoding='utf-8') as json_parameter_file:
			parameters_string = await json_parameter_file.write(f'{parameters}')
			await json_parameter_file.close()

	async def get_video_json(self):
		await log.record("Получение videos.json")
		async with _open(join('plugins/configs', 'videos.json'), "r", encoding = "utf-8") as video_json:
			lines = await video_json.read()
			await video_json.close()
		return eval(f"dict({lines})")
	
	async def save_video_id(self, id):
		if isinstance(id, int):
			await log.record(f"Сохранение video_id: {id}")
			old = await self.get_video_json()
			parameters = await self.get_parameter()
			new = {f"{id}": [time(), parameters["post_live"]]}
			
			async with _open(join('plugins/configs', 'videos.json'), "w", encoding = "utf-8") as video_json:
				
				await video_json.write(f"{new | old}")
				await video_json.close()
				
			await log.record("Видео сохранено")
		elif isinstance(id, dict):
			new = id
			old = await self.get_video_json()
			parameters = await self.get_parameter()
			
			async with _open(join('plugins/configs', 'videos.json'), "w", encoding = "utf-8") as video_json:
				
				await video_json.write(f"{new | old}")
				await video_json.close()
	
	async def video_pool(self):
		await log.record("Запрос к видеофайлам")
		video = await self.get_video_json()

		to_delete = []
		to_save = {}

		items = list(video.items())
		#print(items)

		for video_object in items:
			#print(1)
			video_id = video_object[0]
			video_post_time = video_object[1][0]
			video_live = video_object[1][1]
			
			await log.record(f"Обработка {video_id}")
			
			#print(time() - video_post_time >= video_live, video_id)
			
			if (time() - video_post_time >= video_live):
				await log.record(f"{video_id} на удаление")
				to_delete.append(int(video_id))
			else:
				to_save[video_id] = [video_post_time, video_live]
		
		#print(to_delete)
		if (to_delete != []):
			return to_delete
		else:
			return 0