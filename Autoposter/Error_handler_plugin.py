"""
Название: Плагин обработчика ошибок/Error_handler_plugin.py
Тип: Обработчик ошибок/плагин
Статус: Готов к использованию
Краткое описание: Небольшой обработчик ошибок
"""
import asyncio # Импорт асинхронности

from logging_plugin import Async_logging # Импортируем логгинг

log = Async_logging() # Инициализируем

asyncio.run(log.set_file_name("bot_log.log")) # Меняем название лога

class Error_handler(): # Объявляем класс
	
	def __init__(self):
		self.errors = True # Не используется
	
	async def set_handler(self, parameter: bool):
		self.errors = parameter # Не используется
		await log.record(f"Параметр errors изменён на: {parameter}")
	
	async def handler(self, error = None): # Сам обработчик
		try:
			if (error is None): # Обрабатываем ошибку в ошибке
				await log.record("Ничего не передано!")
				return (0, "Нечего обрабатывать")
			else:
				code = int(error.code)
				"""
	Vkbottle => VKAPIError
	У VKAPIError есть несколько параметров:
			Description
			Code
			Img (только у code == 14)
			Cid (только у code == 14)
				"""
				if (code == 1):
					await log.record("Неизвестная ошибка.") # Ответ сервера ВК
				elif (code == 3):
					await log.record("Неизвестный метод! Проверьте его написание ещё раз. Пожалуйста") # Если кто-то будет пенять мой код. Пишите комментарии!
				elif (code == 5):
					await log.record("Неверный токен. Попробуйте другой...") # Тут я ничего не поделаю
				elif (code == 6):
					await log.record("Слишком много запросов в секунду...") # Никогда не сталкивался с подобной ошибкой
				elif (code == 9): # А эта ошибка вырубает сообщения на полтора часа
					await log.record("Flood control")
				elif (code == 7):
					await log.record("Нет прав для выполнения этого действия") # Токену его не предоставили... Ну, при создании
				elif (code == 8):
					await log.record("Неверный синтаксис запроса.") # Понятия не имею в чём откличие от 3 ошибки
				elif (code == 10):
					await log.record("Ошибка сервера. Повторите запрос позже, пожалуйста") # Тут наши полномочия всё. Кстати в октябре 2021 года была DDOS атака на vk.com, наверное в тот момент у всех летела 10-ая ошибка
				elif (code == 14):
					await log.record("Произошла Captcha") # Img и Cid)
				elif (code == 18):
					await log.record("Страница удалена или заблокирована") # Страница пользователя чей токен
				elif (code == 23):
					await log.record("Метод был выключен") # А вдруг мой код и поддерживаться будет
				elif (code == 100):
					await log.record(f"Не передан какой-то параметр, {error}") # Моя постоянная ошибка
				elif (code == 118):
					await log.record("Неверный сервер") # В POST запросах, хотя врядли оно полетит...
				elif (code == 121):
					await log.record("Хэш фото не верен") # Тоже постоянная ошибка если использовать готовые Uploaders от vkbottle
				elif (code == 214):
					await log.record("Отказано в размещении поста") # ???
				elif (code == 222):
					await log.record("Гиперссылки запрещены") # ???
				else:
					await log.record(f"Неизвестная ошибка номер {code}\n{error}") # Скиньте пожалуйста мне неизвестную ошибку
					return (0, "Просмотрите лог")
		except AttributeError:
			await log.record(f"Передана не ошибка VK API: {error} = {type(error)}")
			return (0, "Не ошибка!")
		except Exception as ex:
			await log.record(f"Что-то пошло не так... {ex}") # ¯\_(ツ)_/¯
			return (0, ex)