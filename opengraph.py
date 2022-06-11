from bs4 import BeautifulSoup as BS
import requests
#import telebot
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
#-------------- Function for general info --------------
async def info_gen(url):
	head = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
	r = requests.get(url, headers=head)# Отправяем запрос с заголовками на сайт
	kurs = {
		'mid': '',
		'ch_today': '',
		'ch_week': '',
		'ch_month': '',
		'ch_fmonth': '',
		'vtf': '',
		'last_deal': '',
	}
	soup = BS(r.text, 'lxml')# просто суп
	# Просто парсим инфу
	kurs['mid'] = soup.select_one('#workarea > div.content_i.converter > div.birzha_info_head_wrap > div:nth-child(1) > div > div.row > div:nth-child(1) > div').text.replace(" ", "").replace('\n', '')
	kurs['ch_today'] = soup.select_one('#workarea > div.content_i.converter > div.birzha_info_head_wrap > div:nth-child(1) > div > div.row > div:nth-child(2) > div').text.replace(" ", "").replace("\n", " ")
	kurs['ch_week'] = soup.select_one('#workarea > div.content_i.converter > div.birzha_info > div > div:nth-child(2) > div.birzha_info_rates').text.replace(" ", "").replace('\n', '')
	kurs['ch_month'] = soup.select_one('#workarea > div.content_i.converter > div.birzha_info > div > a:nth-child(3) > div.birzha_info_rates').text.replace(" ", "").replace('\n', '')
	kurs['ch_fmonth'] = soup.select_one('#workarea > div.content_i.converter > div.birzha_info > div > a:nth-child(4) > div.birzha_info_rates').text.replace(" ", "").replace('\n', '')
	kurs['vtf'] = soup.select_one('#workarea > div:nth-child(5) > div > div > table > tbody > tr:nth-child(4) > td:nth-child(2)').text.replace(" ", "").replace('\n', '')
	kurs['last_deal'] = soup.select_one('#workarea > div:nth-child(5) > div > div > table > tbody > tr:nth-child(8) > td:nth-child(2)').text.replace(" ", "").replace('\n', '')
	name = url[url.rfind('rates/') + 6:]# С ссылки берём название крипты и валюту
	# Запихиваем всю инфу в переменную и возращаем её
	info = f'*{name}*\nОбщая информация:\nСр цена: {kurs["mid"]}\nИзм(24ч): {kurs["ch_today"]}\nИзм(неделя): {kurs["ch_week"]}\nИзм(месяц): {kurs["ch_month"]}\nИзм(3м): {kurs["ch_fmonth"]}\nОбьём(24ч): {kurs["vtf"]}\nПосл сделка(биржа): {kurs["last_deal"]}'
	return info, r.text
#--------------- Function for detail info --------------
async def info_birjes(url, id):
	token = 'token'
	bot = Bot(token=token)
	head = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
	r = requests.get(url, headers=head)
	soup = BS(r.text, 'lxml')
	all_birj = soup.select_one('#crypto_exchange > table > tbody') # В переменную загружаем табличку с биржами
	#all = []
	for i in all_birj:# Создаём цыкл где проходим по всем биржам
		ch = ''
		name = ''
		ssoup = BS(str(i), 'lxml')# Скармливаем супу 
		a = ssoup.find('div', class_="s-bold")# Получаем строку с биржей
		if a != None:
			name = ssoup.find('div', class_="s-bold").find('a').text# Получаем название биржи
			# Записываем в переменную все изменения и отправляем сообщение с ними
			ch = f'*{name}*\nСр курс: {ssoup.select_one("td:nth-child(2)").text}\nМин(24ч): {ssoup.select_one("td:nth-child(3)").text}\nМакс(24ч): {ssoup.select_one("td:nth-child(4)").text}\nИзм: {ssoup.select_one("td:nth-child(5) > span").text} ({ssoup.select_one("td:nth-child(5) > sup").text})\n ' 
			#all.append(ch)
			await bot.send_message(id, ch, parse_mode="Markdown")

#-------------- Main func -------------- (Она здесь есть потому-что раньше это была отдельная прога но я решил засунуть её в тг-бота, не обращайте внимания)
if __name__ == "__main__":
	a = 0