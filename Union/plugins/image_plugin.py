import asyncio

from asyncio import run, create_task, gather
from os import remove
from os.path import join

from image_plugins.image_logger import Logger
from image_plugins.image_binder import Binder

log = Logger()
binder = Binder()

class ImageGenerator:
	
	def __init__(self):
		run(log.begin())

	async def generate(self):
		await log.record(f"Создание и отправка тасков")
		parameters = await binder.get_config()
		request = []
		for num in range(0, parameters['main']['at_time']-1):
			await log.record(f"Запрос {num+1} записан!")
			request.append(create_task(binder.draw_to_image()))
		await log.record(f"Отправка запросов")
		response = await gather(*request)
		return response
		
	async def delete(self, name:str = ""):
		remove(join("Only_images/", name))