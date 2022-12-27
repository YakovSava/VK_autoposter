import asyncio

from asyncio import run, gather, create_task, sleep

from plugins.image_logger import Logger
from plugins.image_binder import Binder

log = Logger()
binder = Binder()

async def sleeper():
	parameters = await binder.get_config()
	await log.record(f"Засыпание на {parameters['main']['sleep']} времени")
	await sleep(parameters['main']['sleep'])

async def task_manager():
	await log.record(f"Создание и отправка тасков")
	parameters = await binder.get_config()
	request = []
	for num in range(0, parameters['main']['at_time']-1):
		await log.record(f"Запрос {num} записан!")
		request.append(create_task(binder.draw_to_image()))
	await log.record(f"Отправка запросов")
	await gather(*request)

async def main():
	while True:
		await task_manager()
		await sleeper()

if __name__ == '__main__':
	run(log.begin())
	run(main())