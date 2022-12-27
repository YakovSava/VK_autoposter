import asyncio

from aiofiles import open as _open
from PIL import Image, ImageDraw, ImageFont
from os.path import join, exists
from os import listdir
from random import choice
from asyncio import run

from plugins.image_logger import Logger

log = Logger()

class Binder:

	def __init__(self):
		self.config_name = 'image_config.json'
		self.standart_path_image = 'Data_to_picture/images/'
		self.standart_path_texts = 'Data_to_picture/texts/'
		self.standart_path_font = 'Data_to_picture/fonts/'
		self.standart_saver_path = 'Datas/'

	async def get_config(self):
		await log.record('Зпрос к файлу конфига')
		async with _open(self.config_name, 'r', encoding = 'utf-8') as config_file:
			data = await config_file.read()
		return eval(f'dict({data})')

	async def get_img(self, img_name:str):
		await log.record('Запрос изображения')
		img = Image.open(join(self.standart_path_image, img_name))
		return img

	async def get_random_img(self):
		await log.record('Запрос рандомного изображения')
		rand_image = choice(listdir(self.standart_path_image))
		return rand_image

	async def get_random_text(self):
		await log.record('Запрос рандомного текста')
		rand_text = choice(listdir(self.standart_path_texts))
		async with _open(join(self.standart_path_texts, rand_text), 'r', encoding = 'utf-8') as rand_file:
			text_in_file = await rand_file.read()
		await log.record(f'Рандомный текст: {text_in_file}\nФайл: {rand_text}')
		return text_in_file

	async def draw_to_image(self):
		await log.record("Запрос рисунка")
		parameters = await self.get_config()
		rand_img, rand_text = await self.get_random_img(), await self.get_random_text()
		image = await self.get_img(rand_img)

		#print(join(self.standart_path_font, f'{parameters["font"]}.ttf'))

		headline = ImageFont.truetype(join(self.standart_path_font, f'{parameters["font"]}.ttf'), size = parameters['size'])
		await log.record("Заголовок сформирован")
		drawer = ImageDraw.Draw(image)
		await log.record("На изображении есть текст")
		image_size = image.size

		image_size_left = image_size[0] * (parameters['edge'] / 100)
		image_size_right = image_size[1] * (parameters['floor'] / 100)

		drawer.text((image_size_left, image_size_right), rand_text, font = headline)
		image.save(join(f'{self.standart_saver_path}/{parameters["main"]["save_in"]}', f'new_{rand_img}'))
		await log.record("Изображение сохранено")