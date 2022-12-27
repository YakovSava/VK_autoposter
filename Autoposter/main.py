"""
Название: main.py/Основной файл
Тип: Основной файл
Статус: Готово к использованию
Краткое описание: Главный файл. Импортирует все плагины
"""
import asyncio # Импорт асинхронности

from vkbottle.user import User # Из асинхронной библиотеки vkbottle, корня user импортируем авторизацию пользователя
from vkbottle import VKAPIError # Из корня vkbottle импортируем ошибки (для их обработки)
from aiohttp import ClientSession, ClientTimeout # Из асинхронной библиотеки веб запросов импортируем сессию клиента
from random import randint, shuffle # из рандома импортируем выбор рандомных цифр и перемешку списка
from os.path import join # Из системы работы с файлами импортируем вхождение в файл

# Импортируем плагины
from Error_handler_plugin import Error_handler
from logging_plugin import Async_logging
from binder_plugin import Binder
from Bot_plugin import Bot, Bot_timer
from tokens import vk_token, group_id

# Объявляем класс группы
class Group():
	
	def __init__(self): # Инициализируем класс
		self.timeout = ClientTimeout(500000)
	
	async def get_hashtags(self):
		await log.record("Получение хэштегов")
		parameter = await binder.get_parameter() 
		raw_hashtags = await binder.get_raw_hashtags() # "Сырой" вид
		await log.record(f"Получены хэштеги: {raw_hashtags}")
		
		if raw_hashtags["code"]: # Если без ошибок (возвращает 1)
			all_hashtags = raw_hashtags["content"] # Все хэштеги
			shuffle(all_hashtags) # Перемешиваем (честно признаюсь, каждый раз как я пишу "shuffle" у меня в голове проигрывается звук ветра. точнее, ну типа "ВШВШВШВШВШШШШШВШВШВ")
			returned_hashtags = []
			#print(all_hashtags)
			returned_hashtags.append(all_hashtags[:parameter['hashtags']['hashtags_quantity']])
			await log.record("Обработка хэштегов завершена")
			return returned_hashtags
			
	async def delete_post(self, list_to_delete:list=[]):
		try:
			await log.record("Удаление постов...")
			if (isinstance(list_to_delete, list)) and (list_to_delete == []):
				await log.record("Список на удаление пуст")
				return 1
			else:
				if isinstance(list_to_delete, list):
					await log.record("Запуск цикла...")
					stop_counter = 0
					await log.record("Объявление счётчика")
					for post_id in list_to_delete:
						if (stop_counter != 3):
							await log.record(f"Удаление поста {post_id}")
							await vk.api.wall.delete(
									owner_id = -group_id,
									post_id = post_id)
							await log.record("Пост удалён")
						else:
							await log.record("Ожидание...")
							await asyncio.sleep(3)
							stop_counter = 0
			return 1
		except VKAPIError as vk_api_error:
			await if_error.handler(vk_api_error)
			return 0
	
	async def repost(self): # Функция репоста
		try:
			await log.record("Получение хэштегов") # Всё в лог идёт
			repost_hashtags = "#repost " # Начало хэштегов
			hashtags = await self.get_hashtags()
			#print(hashtags)
			for hashtag in hashtags[0]:
				repost_hashtags += f"{hashtag} "
			
			donors = await binder.get_donors() # Получаем доноров
			await log.record("Доноры получены")
			if donors[0]: # Если без ошибок
				donor = donors[1] # Список доноров
				shuffle(donor) # Перемешиваем
				
				await log.record(f"Получение поста донора - {donor[0]}")
				
				posts = await vk.api.wall.get(domain = donor[0], count = 20) # Получаем посты. Новые
				post_info = dict(dict(posts)['items'][randint(0, len(dict(posts)['items'])-1)]) # Берём рандомный пост. Структура сложная...
				
				post_id = post_info['id'] # Получаем id поста
				group_id1 = post_info['owner_id'] # Получаем id группы
				
				await log.record("Получен объект")
				
				wall_object = f"wall{group_id1}_{post_id}" # Создаём объект
				
				msg = ""
				
				parameter = await binder.get_parameter()

				if parameter['hashtags']['hashtags_repost']:
					msg += repost_hashtags
				
				repost_id = dict(await vk.api.wall.repost( # Подучаем id поста
								group_id = abs(group_id),
								object = wall_object, 
								message = msg))['post_id']
				return repost_id # Возвращаем
		except VKAPIError as vk_api_error:
			await if_error.handler(vk_api_error) # Обработка ошибок
	
	# Получение сервера
	async def get_server(self, attachments: list = []):
		try:
			list_of_images = [] # Хоть один, хоть 10, программе пофиг, пост будет
			await log.record("Сервер получен...")
			
			# Открываем сессию aiohttp
			async with ClientSession() as session:
				await log.record("Открыта сессия")
				for attachment in attachments: # Запускаем цикл внутри сессии
					#print(attachment)
					if (attachment[0] != 'video'):
						#print("photo trigger")
						photo_server_link = dict(await vk.api.photos.get_wall_upload_server(group_id = group_id)) # Получаем сервер
						#print(photo_server_link)
						async with session.post( # POST запрос на сервер
							photo_server_link['upload_url'],
							data = {"photo": open( # Передаём фото
								join(
									attachment[0],
									attachment[1]),
								"rb")
							},
							timeout = self.timeout
						) as post_response:
							await log.record("POST запрос выполнен")
							resp = await post_response.read() # Читаем
							list_of_images.append(resp)
					elif (attachment[0] == "video"):
						#print("video trigger", attachment)
						video_server_link = dict(await vk.api.video.save(
								name = "Video",
								description = "Description",
								wallpost = 0,
								group_id = group_id,
								repeat = 0))
						async with session.post(
						video_server_link["upload_url"],
						data = {"video": open(
							join(
								attachment[1],
								attachment[2]),
							"rb"
						)},
						timeout = self.timeout
						) as post_response:
							await log.record("POST запрос выполнен")
							resp = await post_response.read() # Читаем
						"""
		Почему "await post_response.read()", а не "resp = await post_response.json()"? Сейчас объясню!
		в этом POST запросе возвращается строка вида: a=5, b=4 (там нет ни a, ни b, это лишь пример) и json.loads(object) банально не обрабатывает подобное, ну и саму строку с помощью dict() никак не преобразовывать. Но немного порвышись в интернете, я нашёл решение этого странного и довольно редкого случая. См. следущую функцию
						"""
						list_of_images.append(["video", resp]) # Добавляем ответы сервера
					await log.record("Результаты прочитаны")
			await log.record("Сессия закрыта")
			#print(list_of_images)
			try:
				return (list_of_images, photo_server_link['user_id'], video_server_link['owner_id']) # Возвращаем результат
			except UnboundLocalError:
				try:
					return (list_of_images,  video_server_link['owner_id'])
				except UnboundLocalError:
					try:
						return (list_of_images,  photo_server_link['user_id'])
					except UnboundLocalError:
						return [0]
		except VKAPIError as vk_api_error:
			await if_error.handler(vk_api_error) # Обработка возможных ошибок
	
	# Пост на стену
	async def post_on_wall(self, text = "", attachments = []):
		try:
			parameters = await binder.get_parameter()
			post_hashtags = "" # Хэштеги
			hashtags = await self.get_hashtags()
			#print(hashtags)
			for hashtag in hashtags[0]:
				post_hashtags += f"{hashtag} "

			await log.record("Пост на стену...")
			
			#print(attachments)
			response = await self.get_server(attachments) # Получаем сервер
			#print(response)

			if parameters['hashtags']['hashtags_post']:
				text += f"\n\n{post_hashtags}" # Добавляем хэштеги
			
			media_link = "" # Правильней было бы назвать media_links, но я ленивый)
			
			#print(response)
			if not response[0]:
				post_id = dict(await vk.api.wall.post( # Отправляем пост на стену, 
										owner_id = -group_id,
										message = text,
										from_group = 1))['post_id']
				return post_id
			else:
				for server_response in response[0]:
					if (server_response[0] != 'video'):
						userid = response[1]
						await log.record("Преобразование данных") # Сообщение лога вместо комментария
						#print(server_response)
						resp_string = server_response.decode() # Декодируем байт-строку
						response_dictionary = eval(f"dict({resp_string})")

						"""
					А вот и то самое решение моего редкого и странного случая. Я просто с помощью eval() (Выполнение строки) выполняю действие преобразования ключевых аргументов (a=5, b=6) в словарь ({"a": 5, "b": 6})
						"""
						#print(response_dictionary)
						# Для красоты разбиваем на переменные
						server = response_dictionary['server']
						photo = response_dictionary['photo']
						hash = response_dictionary['hash']
						
						await log.record("Загрузка фото")
						photo_information = dict((await vk.api.photos.save_wall_photo(group_id = group_id, # Сохраняем фото
												photo = photo,
												server = server,
												hash = hash))[0])
						photo_id = photo_information["id"]
						# Получаем photo_id
						
						await log.record("Фото загружено!\nПолучение ссылки...")
						media_link += f"photo{userid}_{photo_id}," # Формируем ссылку. Даже если фото одно, "," никак не мешает
					elif (server_response[0] == 'video'):
						#print(server_response, "video trgger")
						resp_string = server_response[1]
						response_dictionary = eval(f"dict({resp_string.decode()})")
						#print(response_dictionary)
						video_id = response_dictionary["video_id"]
						userid = response_dictionary["owner_id"]

						await binder.save_video_id(video_id)
						
						media_link += f"video{userid}_{video_id},"
				
				await log.record("Пост отправляется на стену...")
			
				#print(media_link)
				post_id = dict(await vk.api.wall.post( # Отправляем пост на стену, 
										owner_id = -group_id,
										attachments = media_link,
										message = text,
										from_group = 1))['post_id']
				await log.record("Пост на стене!")

				return post_id # Возвращаем post_id
		except VKAPIError as vk_api_error:
			await if_error.handler(vk_api_error) # Обрабатываем возможные ошибки

	async def delete_video(self, list_video_ids_to_delete:list):
		counter = 0
		for video_id in list_video_ids_to_delete:
			try:
				counter += 1
				await vk.api.video.delete(
										video_id = video_id,
										owner_id = -group_id)
			except VKAPIError as vk_api_error:
				await if_error.handler(vk_api_error)
			if counter >= 2:
				await asyncio.sleep(2)
				counter = 0
		await log.record('Удаление видео завершено')

# Инициализируем классы
if_error = Error_handler()
log = Async_logging()
binder = Binder()
group_bot = Group()
timer = Bot_timer() # Наследование не сработало, поэтому пришлось отдельно инициализировать таймер и бота
bot = Bot()

vk = User(token = vk_token)

# Функция "обёртка"
async def photo_on_wall(pool_counter):
	#print(pool_counter)
	send_to_post = {}
	file_exist = await binder.poll(pool_counter) # Пул если есть какие то папки
	if file_exist[0]:
		#print(file_exist)
		check0, check1 = file_exist[1][0], file_exist[1][1]
		if isinstance(check0, list):
			send_to_post["photo"] = check0
		elif isinstance(check0, str):
			send_to_post["text"] = check0
		if isinstance(check1, list):
			send_to_post["photo"] = check1
		elif isinstance(check1, str):
			send_to_post["text"] = check1
		try:
			intermediate_result = await group_bot.post_on_wall( #Промежуточный результат в обёртке
				text = send_to_post["text"],
				attachments = send_to_post["photo"])
			return intermediate_result # Возвращаем промежуточный результат
		except KeyError:
			await log.record(f"Переданы неизвестные аргументы: {type(file_exist[1][1])}\n{type(file_exist[1][0])}")
	else:
		await log.record(file_exist[1]) # Неизвестная ошибка

# "Обёртка бота"
async def bot_run(counter=False, pool_counter=0):
	parameters = await binder.get_parameter() # Получаем параметры
	if parameters['posts']["post"]:
		if counter:
			if parameters['posts']["repost"]:
				await log.record("Репост!") # Это репост
				postid = await group_bot.repost() # Бот вызывает репост
		else:
			if parameters['posts']['post']:
				await log.record("Пост!") # Это пост
				postid = await photo_on_wall(pool_counter) # Бот вызывает "обёртку"
		#print(postid)
	await bot.remember_time_of_post(postid, parameters['post_live']) # Сохраняем данные
	to_delete = await bot.pool() # Пул бота (проверка)
	if not isinstance(to_delete, int):
		await group_bot.delete_post(to_delete)
	
	to_video_delete = await binder.video_pool()
	#print(to_video_delete)
	if not isinstance(to_video_delete, int):
		await group_bot.delete_video(to_video_delete)
	
	await bot.go_sleep(parameters['post_time']) # Бот засыпает на N-ное кол-во времени

# Основная функция
async def main():
	print("Запуск...")
	await log.set_file_name("bot_log.log") # Объявляем название лога
	await log.begin() # Стриаем прошлые записи
	await log.record("Бот запущен")
	#to_video_delete = await binder.video_pool()
	#print(to_video_delete)
	counter = 0
	pool_counter = 0
	while True: # Запускаем бота в бесконечном цикле
		counter_stop = await binder.get_parameter() # Получаем параметры
		if counter_stop['folder_order_length'] <= pool_counter:
			pool_counter = 0

		if counter_stop["posts"]['post']: # Если посты включены
			if counter_stop['posts']['repost']: # Если репосты включены
				if counter == counter_stop["post_repost"]:
					await bot_run(counter=True, pool_counter=pool_counter)
					counter = 0

				else:
					await bot_run(pool_counter=pool_counter)
					counter += 1

			else: # Если отключены то впринципе, а зачем отправлять пулы с репостами?
				await bot_run(pool_counter=pool_counter)

		pool_counter += 1

	
if __name__ == "__main__": # Проверка: запускаем ли мы этот файл
	asyncio.run(main()) # Вызываем основную функцию