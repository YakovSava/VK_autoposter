"""
Название: Bot_plugin.py/Плагин бота
Тип: Плагин
Статус: Готов к использованию
Краткое описание: Плагин для бота и таймера. Тут наследование и не получилось
"""
import asyncio # Асинхронность

from time import time # Импортируем функцию для времени с начала эпохи (01.01.1970)
from asyncio import sleep, run # Из асинхронности для красоты, импортируем некоторые иные функции
from aiofiles import open as _open # Импортируем асинхронное открытие файлов и дабы не было ошибок добавляем "_"
from random import randint # Из рандома импортируем рандомный цифры
from warnings import filterwarnings # Из предупреждений импортируем фильтр...

from logging_plugin import Async_logging # Асинхронный логгинг

filterwarnings("ignore") # ...и игнорим все предупреждени
log = Async_logging() # Инициализация

# Объявляем класс
class Bot_timer():
	
	def __init__(self): # Инициализация
		run(log.set_file_name("autobot_log.log")) # Изменяем название лога
		run(log.begin()) # Стираем прошлый лог
		run(log.record(f"Создан объект бота!\n")) # Первая запись в лог
	
	# Все функции асинхронные, начинаем объявлять их
	async def set_timer(self, times:int): # Сетаем рандомный таймер
		await log.record("Таймер отправлен")
		return sleep(times)

timer = Bot_timer()
"""
--------------------------------------------------------
class Bot(Bot_timer):
	
	...
	
	async def go_sleep(self):
		bot_dream = await self.set_timer()
		await bot_dream
--------------------------------------------------------
AttributeError: object "Bot" has no attribute "set_timer"
--------------------------------------------------------
Думаю по этому комментарию я объяснил почему мне пришлось прямо тут и инициализировать класс таймера
"""

# Объявляем класс бота
class Bot():
	
	# Инициализация бота
	def __init__(self):
		self.post_time = {} # Это нужно уже
	
	# Для того что бы бот заснул на N-ное количество секунд
	async def go_sleep(self, times):
		bot_dream = await timer.set_timer(times) # "Сны бота" :)
		await bot_dream
		"""
	Объяснять как работают корутины не нужно? Хотя я не имею представления кто бужет читать мой код, поэтому распишу:
		Корутину (Coroutine) можно объявить как функцию:
		async def test_function():
			print("I'm a test function!")
		Это получается асинхронная функция, её можно записать в переменную как:
			variable = test_function
		И как:
			variable = test_function()
		Это асинхронная функция, поэтому "test_function()" не вызовет её, зато вызовет предупреждение RuntimeWarning (поэтому я отключил предупреждения впринципе)
		Как же вызвать асинхронную функцию? Необходимо использовать "await" или "asyncio.run" (последнее для перехода от синхронности, в асинхронность)
	Пример:
--------------------------------------------------------
import asyncio

async def test_function():
	print("I'm a test function!")

variable0 = test_function
variable1 = test_function()
		
async def function_call():
	await variable0()
	await variable1

if __name__ == "__main__":
	asyncio.run(function_call())
	asyncio.run(variable0())
	asyncio.run(variable1)
--------------------------------------------------------
Но стоп, у нас вылетает ошибка: "RuntimeError: cannot reuse already awaited coroutine", почему? Она выскакивает на 16 строке кода (asyncio.run(variable1)) т.е. мы повторно вызываем уже ожидаемую функцию (© Гугл переводчик), но вот variable0() ваше пофиг на такое.
--------------------------------------------------------
Что в нашем случае? Тут мы постоянно создаём новые корутины, поэтому ошибки RuntimeError быть не должно. Если же будет напишите мне пожалуйста.
		"""
	
	async def remember_time_of_post(self, post_id:str, times:int): # "Регистрация" поста
		self.post_time[str(post_id)] = [time(), times] # Немного использования self.post_time
		json_file_not_in_file = self.post_time
		await log.record(f"Для поста {post_id} задано время {times}")
		json_text = await self.get_json() # Получаем json
		async with _open("posts.json", "w", encoding='utf-8') as json_file: # Чистим старый, создаём новый
			#print(json_text|json_file_not_in_file)
			await json_file.write(f"{json_text|json_file_not_in_file}") # Используем добавленный в 3.9 оператор объединения, для... объединения словарей (|)
			await json_file.close()# Закрываем json файл
	
	async def pool(self): # Пул реквест
		text = {} # Текст = словарь
		posts = await self.get_json() # Получаем посты
		to_delete = [] # Сюда запишем посты на удаление (хотел пошутить: "Расстрельный список")
		for post in posts.items(): # Включаем цикл, в нём перебираем объекты posts
			post_id = post[0] # Для красоты создаём переменнные
			post_time = post[1][0]
			remaining_post_time = post[1][1]
			if (time() - post_time >= remaining_post_time): # Если срок поста истёк
				to_delete.append(post_id) # Добавляем его в список на удаление
				#print(post_id, time() - post_time, (time() - post_time >= remaining_post_time))
				continue
			else:
				text[str(post_id)] = [post_time, remaining_post_time] # Если же пост не на удаление
		for post_id_to_delete in to_delete:
			try:
				del text[post_id_to_delete]
			except KeyError:
				continue
		async with _open("posts.json", "w", encoding='utf-8') as json_file: # Записываем обратно в JSON
			await json_file.write(f"{text}")
			await json_file.close()
		
		#print(to_delete)
		
		if (to_delete != []): # А возвращать ли нам список?
			return to_delete
		else:
			return 0
	
	async def get_json(self): # Получение JSON
		try:
			async with _open("posts.json", "r", encoding='utf-8') as json_file:
				resp = await json_file.read() # Читаем его
				await json_file.close() # Закрываем файл
			to_return = eval(f"dict({resp})") # Выполняем (с json.loads у меня чёт ошибка JSONDecodeError, хотя ничего такого нет. На Stackoverflow сказали что мб файл битый, но нет, он не был битым)
			return to_return # Возвращаем
		except FileNotFoundError:
			pass # Это для первого запуска