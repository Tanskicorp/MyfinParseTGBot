import sqlite3
import re
import asyncio
from aiogram import Bot, Dispatcher, executor, types
import aiohttp

token = 'token'
bot = Bot(token=token)

async def spisok(id):
	with sqlite3.connect('favorite.db') as db:
		cursor = db.cursor()
		query = """
		CREATE TABLE IF NOT EXISTS fav(
		id TEXT,
		url TEXT
		)
		"""
		cursor.execute(query)
		db.commit()
		cursor.execute("SELECT * FROM fav WHERE id = ?", [id])
		if cursor.fetchone() is None:
			await bot.send_message(id, "У вас нет подписок")
			return 'no'
		else:
			await bot.send_message(id, 'Список ваших подписок:')
			cursor.execute("SELECT * FROM fav WHERE id = ?", [id])
			p = cursor.fetchall()[0][1].split(';')
			#print(p)
			for i in p:
				await bot.send_message(id, i.replace('https://myfin.by/crypto-rates/', ''))

async def fav_remove(id, crypt):
	with sqlite3.connect('favorite.db') as db:# Подключаемся к базе данных
		url = []
		for i in crypt.split(" "):
			url.append(f'https://myfin.by/crypto-rates/{i}')
		print(url)
		cursor = db.cursor()# Курсор
		# Таблица
		query = """
		CREATE TABLE IF NOT EXISTS fav(
		id TEXT,
		url TEXT
		)
		"""
		cursor.executescript(query)# Здесь запускаем скрипт таблички
		db.commit()# Подтверждаем
		cursor.execute("SELECT id FROM fav WHERE id = ?", [id])# Выбираем столбец айди, и ищем в нём поле с айди пользователя
		if cursor.fetchone() is None:# Если такой строчки нет, выводим
			await bot.send_message(id, "Вы не подписаны не на одну валюту")
			return
		else:# Если есть, то проверяем статус подписки
			cursor.execute("SELECT * FROM fav WHERE id = ?", [id])# Выбираем строку с айди пользователя
			sub = cursor.fetchall()[0][1].split(';')
			print(str(sub) + ' SUB')
			acheck = len(sub)
			#print(acheck)
			bcheck = 0
			for i in url:
				bcheck = 0
				#print(url)
				#print(sub)
				#print(i)
				for j in sub:	
					#print(j)
					if j == i:
						break
					else:
						bcheck = bcheck + 1
				if bcheck >= acheck:
					#print(i)
					await bot.send_message(id, f"Вы не подписаны на валюту {i.replace('https://myfin.by/crypto-rates/', '')}")
					del url[url.index(i)]
			if len(url) == 0:
				return
			else:# иначе
				cursor.execute("SELECT * FROM fav WHERE id = ?", [id])# Выбираем строку с айди пользователя
				rem_sub = cursor.fetchone()[1]# Записываем строку в переменную
				rem_sub = re.sub(r'[;]{2,}', r';', rem_sub).split(';')# Убираем повторения ";", и разделяем ссылки на массив
				for i in url:
					for j in rem_sub:
						if i == j:
							del rem_sub[rem_sub.index(j)]
							break
				rem_sub = ";".join(map(str, rem_sub))# Соединяем массив обратно
				#print(rem_sub)
				if rem_sub == '':# Если ссылок больше нет
					cursor.execute("DELETE FROM fav WHERE id = ?", [id])# То удаляем строку с пользователем
					db.commit()# Подтверждаем и выводим
					await bot.send_message(id, "У вас больше не осталось подписок")
					return
				# Если ссылки всётаки есть, то убираем лишние ;
				if rem_sub[0] == ';':
					rem_sub = rem_sub[1:]
				if rem_sub[-1] == ';':
					rem_sub = rem_sub[:-1]
				cursor.execute("UPDATE fav SET url = ? WHERE id = ?", (rem_sub, id))# Записываем новую ячейку без удалённой ссылки
				db.commit()# Сохраняем
				await bot.send_message(id, f"Вы успешно отписались от {' '.join(map(str, url)).replace('https://myfin.by/crypto-rates/', '')}")
				return
		cursor.execute("SELECT * FROM fav")# Выбираем все данные с таблички
		row = cursor.fetchall()# Записываем все строчки в переменную
		for i in row:# Выводим по очереди
			print(i)

async def fav_add(id, url):
	print(url)
	if 'https://m.myfin.by/crypto-rates/' in url:
		url = url.replace('https://m.myfin.by/crypto-rates/', 'https://myfin.by/crypto-rates/')
	with sqlite3.connect('favorite.db') as db:# Подключаемся к базе данных
		cursor = db.cursor()# Курсор
		# Таблица
		query = """
		CREATE TABLE IF NOT EXISTS fav(
		id TEXT,
		url TEXT
		)
		"""
		cursor.executescript(query)# Здесь запускаем скрипт таблички
		db.commit()# Подтверждаем
		cursor.execute("SELECT id FROM fav WHERE id = ?", [id])# Выбираем столбец айди, и ищем в нём поле с айди пользователя
		if cursor.fetchone() is None:# Если такой строчки нет, то создаём
			rem_sub = re.sub(r'[;]{2,}', r';', url)# На всякий убираем лишние ;
			if rem_sub[0] == ';':
				rem_sub = rem_sub[1:]
			if rem_sub[-1] == ';':
				rem_sub = rem_sub[:-1]
			cursor.execute("INSERT INTO fav(id, url) VALUES(?, ?)", (id, rem_sub))# Записываем в строку айди и юрл
			db.commit()# Подтверждаем
			await bot.send_message(id, f"Вы успешно подписались на {url.replace('https://myfin.by/crypto-rates/', '')}")
		else:# Если есть, то проверяем статус подписки
			cursor.execute("SELECT * FROM fav WHERE id = ?", [id])# Выбираем строку с айди пользователя
			if url in cursor.fetchone()[1].split(';'):# Если юрл есть уже в списке подписок то выводим надпись
				await bot.send_message(id, "Вы уже подписаны")
				#return
			else:#
				nurl = f";{url}"# Ссылка с раздлительным знаком
				cursor.execute("UPDATE fav SET url = url || ? WHERE id = ?", (nurl, id))# Обновляем данные в поле юрл в строчке пользователя
				db.commit()# Сохраняем
				cursor.execute("SELECT * FROM fav WHERE id = ?", [id])# Выбираем юрл со строчки пользователя
				rem_sub = cursor.fetchone()[1]# Сохраняем юрл в переменную
				rem_sub = re.sub(r'[;]{2,}', r';', rem_sub)# Убираем лишние ;
				if rem_sub[0] == ';':
					rem_sub = rem_sub[1:]
				if rem_sub[-1] == ';':
					rem_sub = rem_sub[:-1]
				cursor.execute("UPDATE fav SET url = ? WHERE id = ?", (rem_sub, id))# Обновляем поле юрл в строчке пользователя
				db.commit()
				await bot.send_message(id, f"Вы упешно подписались на {url.replace('https://myfin.by/crypto-rates/', '')}")
		#cursor.execute("SELECT * FROM fav")# Выбираем все данные с таблички
		#row = cursor.fetchall()# Записываем все строчки в переменную
		#await bot.send_message(id, 'Список ваших подписок:')
		#for i in row:# Выводим по очереди
		#await bot.send_message(id, i[1].replace('https://m.myfin.by/crypto-rates/', '').replace(';', '\n'))

async def people():
	with sqlite3.connect('favorite.db') as db:
		cursor = db.cursor()
		cursor.execute("SELECT * FROM fav")
		all = cursor.fetchall()
		return all
		


if __name__ == '__main__':
	a = 0