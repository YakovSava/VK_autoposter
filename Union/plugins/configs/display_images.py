def get_config():
	with open('image_config.json', 'r', encoding = 'utf-8') as file:
		lines = file.read()
	return eval(f'dict({lines})')

def save_config(new):
	with open('image_config.json', 'w', encoding = 'utf-8') as file:
		file.write(f'{new}')

def edit_config(key, new):
	dictionary = get_config()
	if isinstance(dictionary[key], int):
		dictionary[key] = int(new)
	else:
		dictionary[key] = new
	save_config(dictionary)

def edit_config_main(key, new):
	dictionary = get_config()
	if isinstance(dictionary['main'][key], int):
		dictionary['main'][key] = int(new)
	else:
		dictionary['main'][key] = new
	save_config(dictionary)

def display_config():
	config = get_config()
	print(f'''{'*' * 45}
Редактировать относительно края: {config['edge']} (edge)
Редактировать относительно низа: {config['floor']} (floor)
Размер: {config['size']} (size)
Шрифт: {config['font']} (font)

main:
	Засыпать на {config['main']['sleep']} секунд (main - sleep)
	За раз делать {config['main']['at_time']} изображений (main - at_time)

Цвет текста: {config['text_color']} (RGBA; 'text_color')
{'*' * 45}''')

def edit_color_text():
	dictionary = get_config()
	r = int(input("Введите красный: "))
	g = int(input("Введите зелёный: "))
	b = int(input("Введите синий: "))
	a = int(input("Введите прозрачность: "))
	dictionary['text_color'] = [r, g, b, a]
	save_config(dictionary)

def terminal():
	try: 
		who = str(input('Введите команду: ')).lower()
		if who == 'info':
			print('''
	info - Отображает все команды
	display - Отобразить конфиг
	edit - Редактировать конфиг
		edit - main - Редактировать объект внутри main, конфига
	''')
		elif who == 'display':
			display_config()
		elif who == 'edit':
			edit_what = str(input('Введите ключ редактируемого параметра: ')).lower()
			if edit_what != 'main' and edit_what != 'text_color':
				edit_who = str(input('Введите на что надо редактировать: '))
				edit_config(edit_what, edit_who)
			elif edit_what == "main":
				edit_what2 = str(input('Введите ключ редактируемого параметра внутри main: ')).lower()
				edit_who = str(input('Введите на что надо редактировать: '))
				edit_config_main(edit_what2, edit_who)
			elif edit_what == 'text_color':
				edit_color_text()
		else:
			print(f'Команда {who} не существует...')
	except KeyError as e:
		print(f'Такого параметра нет\n\n{e}')

def main():
	while True:
		terminal()

if __name__ == '__main__':
	main()