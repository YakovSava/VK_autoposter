import asyncio

from aiofiles import open as _open
from datetime import datetime
from time import time

ftst = datetime.fromtimestamp

async def get_json():
	async with _open("posts.json", "r", encoding = "utf-8") as json:
		lines = await json.read()
		await json.close()
	dictionary = eval(f"dict({lines})")
	return dictionary

async def get_information():
	async with _open("config.json", "r", encoding = "utf-8") as datas:
		lines = await datas.read()
		await datas.close()
	dictionary = eval(f"dict({lines})")
	return dictionary

async def get_video():
	async with _open("videos.json", "r", encoding = "utf-8") as datas:
		lines = await datas.read()
		await datas.close()
	dictionary = eval(f"dict({lines})")
	return dictionary

async def save(file, lines):
	async with _open(file, "w", encoding = "utf-8") as newfile:
		await newfile.write(lines)
		await newfile.close()

async def display_videos(lines):
	for item in list(lines.items()):
		#print(item)
		print(f"Видео (id): {item[0]}\nЗапощено в: {ftst(item[1][0])}\nВидео жить (секунды): {item[1][1]}\nВидео ОСТАЛОСЬ жить: {time() - item[1][0]} секунд\n\n")

async def display_posts(lines):
	for item in list(lines.items()):
		#print(item)
		print(f"Пост (id): {item[0]}\nЗапощено в: {ftst(item[1][0])}\nПосту жить (секунды): {item[1][1]}\nПосту ОСТАЛОСЬ жить: {time() - item[1][0]} секунд\n\n")

async def display_information(parameters):
	#print(item)
	print(f'''Посты: {bool(parameters['posts']['post'])} (posts - post)
Репосты: {bool(parameters['posts']['repost'])} (posts - repost)
Промежуток между постами: {parameters['post_time']} (post_time)
Репост каждый {parameters['post_repost']} пост (post_repost)
Каждый пост живёт {parameters['post_live']} секунд (post_live)
Хэштеги в постах {bool(parameters['hashtags']['hashtags_post'])} (hashtags - hashtags_post)
Хэштеги в репостах {bool(parameters['hashtags']['hashtags_repost'])} (hashtags - hashtags_repost)
Количество хэштегов {parameters['hashtags']['hashtags_quantity']} (hashtags - hashtags_quantity)
Количество папок в "Datas/": {parameters['folder_order_length']}
Как распологать эти папки: {parameters['folder_order']}
''')

async def edit_info(parameter:str, edit_to):
	info = await get_information()
	info[parameter] = edit_to
	await save("config.json", f"{info}")

async def edit_post(id:int, edit_to:int):
	all_posts = await get_json()
	all_posts[f"{id}"] = edit_to
	await save("posts.json", f"{all_posts}")

async def edit_video(video_id, edit_to):
	all_videos = await get_video()
	all_videos[f"{id}"] = edit_to
	await save("videos.json", f"{all_videos}")

async def edit_parameter_special(parameter0:str, parameter1:str, edit_to):
	info = await get_information()
	info[parameter0][parameter1] = edit_to
	await save("config.json", f"{info}")

async def edit_parameter_folder_order():
	to_record = []
	parameters = await get_information()
	edit_to = 'folder_order'
	for index in range(0, parameters['folder_order_length']):
		intermediate_result = int(input(f'''Введите какая папка будет идти {index} по счёту.
Учтите что счёт нужно начинать с нуля. Т.е. 0,1,2,3,4 для 5 папок
'''))
		to_record.append(intermediate_result)

	parameters[edit_to] = to_record

	await save('config.json', f'{parameters}')

async def terminal():
	command = str(input("Команда: ")).lower()
	if (command == "info"):
		print("""Все команды:
info - Отобразить все команды
edit - Редактировать что-то
	edit << info - Редактировать параметры
	edit << post - Редактировать время поста
	edit << video - Редактировать время видео
display - Отобразить что-то
	display << info - Отобразить параметры
	display << post - Отобразить время поста
	display << video - Отобразить время видео""")
	elif (command == "edit"):
		who = str(input("Редактировать что: ")).lower()
		if (who == "info"):
			edit_info_parameter = str(input("Введите редактируемый параметр: "))
			print(((edit_info_parameter != 'posts') and (edit_info_parameter != 'hashtags') and (edit_info_parameter != 'folder_order')))
			if ((edit_info_parameter != 'posts') and (edit_info_parameter != 'hashtags') and (edit_info_parameter != 'folder_order')):
				try:
					edit_info_edit_to = int(input("Введите на что редактировать\n\n0 - False, 1 - True\n\n"))
				except ValueError:
					print('На такое редактировать нельзя!')
					return 0
				await edit_info(edit_info_parameter, edit_info_edit_to)
			elif ((edit_info_parameter == 'posts') or (edit_info_parameter == 'hashtags')):
				edit_info_parameter1 = str(input(f'Введите редактируемый параметр внутри параметра {edit_info_parameter}: '))
				try:
					edit_info_edit_to = int(input("Введите на что редактировать\n\n0 - False, 1 - True\n\n"))
				except ValueError:
					print('На такое редактировать нельзя!')
					return 0
				await edit_parameter_special(edit_info_parameter, edit_info_parameter1, edit_info_edit_to)
			elif (edit_info_parameter == 'folder_order'):
				await edit_parameter_folder_order()
		elif (who == "post"):
			edit_post_id = int(input("Введите id поста: "))
			edit_post_time = int(input("Введите оставшееся время поста (в секундах): "))
			intermediate_response = await get_json()
			try:
				await edit_post(edit_post_id, [intermediate_response[f'{edit_post_id}'], edit_post_time])
			except KeyError:
				print(f'Поста {edit_post_id} не существует')
		elif (who == 'video'):
			edit_video_id = int(input("Введите id поста: "))
			edit_video_time = int(input("Введите оставшееся время поста (в секундах): "))
			intermediate_response = await get_video()
			try:
				await edit_video(edit_video_id, [intermediate_response[f'{edit_video_time}'], edit_video_time])
			except KeyError:
				print(f'Поста {edit_video_time} не существует')
		else:
			print(f'Команды edit << "{who}" не существует')
	elif (command == "display"):
		who = str(input("Отобразить что: ")).lower()
		if (who == "info"):
			lines = await get_information()
			await display_information(lines)
		elif (who == "post"):
			lines = await get_json()
			await display_posts(lines)
		elif (who == "video"):
			lines = await get_video()
			await display_videos(lines)
		else:
			print(f'Команды display << "{who}" не существует')
	else:
		print(f'Комманды "{command}" не существует')

async def main():
	while True:
		await terminal()

if __name__ == "__main__":
	asyncio.run(main())