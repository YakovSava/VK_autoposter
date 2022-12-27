import asyncio

from aiofiles import open as _open

class Logger:

	def __init__(self):
		self.log_file_name = 'image_log.log'

	async def begin(self):
		async with _open(self.log_file_name, 'w', encoding = 'utf-8') as logger:
			logger.write('')

	async def record(self, record:str):
		async with _open(self.log_file_name, 'a', encoding = 'utf-8') as logger:
			await logger.write(f'{record}\n')