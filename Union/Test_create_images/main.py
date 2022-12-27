from asyncio import run
from time import time
from datetime import datetime

from image_plugin import ImageGenerator

ftsp = datetime.fromtimestamp
generator = ImageGenerator()

async def main():
	start = time()
	await generator.generate()
	end = time()
	print(f'''
Начало {ftsp(start)}
Конец {ftsp(end)}
Заняло {end - start}
''')

if __name__ == '__main__':
	run(main())