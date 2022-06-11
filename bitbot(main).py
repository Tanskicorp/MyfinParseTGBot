#import telebot
#from telebot.async_telebot import AsyncTeleBot
import opengraph
from bs4 import BeautifulSoup as BS
import requests
#from telebot import types
import time
from requests.exceptions import MissingSchema, InvalidURL, Timeout, InvalidSchema
#import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
import aiohttp
import db_fav
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

token = 'token'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)
db = {}
db2 = {}
url = ''


class InputUserData(StatesGroup):
	step_1 = State()


#------------- /start ------------
@dp.message_handler(commands = ['start'])
async def start(message):
	await message.answer(f'Привествую @{message.from_user.username}! Я бот-парсер курса крипты с сайта myfin.\nПросто вставь ссылку на интересующую валюту и я дам тебе инфу!')


@dp.message_handler(commands = ['help'])
async def help(message):
	await message.answer('Вот список комманд:')
	await message.answer('/crypt ссылка* - получить информацию по крипте')
	await message.answer('Если хотите получить информацию отдельно по биржам, то нажмите "Да", после комманды /crypt ссылка*')
	await message.answer('Если хотите добавить крипту в подписки, то нажмите кнопку "Подписаться" после комманды /crypt ссылка*')
	await message.answer('Если вы подписаны на валюту, то основная инормация по ней будет приходить к вам каждых 10 минут')
	await message.answer('Если хотите узнать список ваших избранных, или отписаться, то введите команду /menu')
	await message.answer('Если в процессе отписки вы передумали отписываться, то напишите /cancel')
	await message.answer('ссылка* - ссылка на курс крипты сайта https://myfin.by/')

#------------------Основная инфа по крипте-----------------
@dp.message_handler(commands = ['crypt'])
async def crypt(message):
    global r
    url = message.text.split(maxsplit=1)[1]# Убираем первое слово с сообщения (/crypt) и получаем ссылку
    db[message.from_user.id] = url
    #print(message.from_user.id)
    #print(url)
    try:
    	info, r = await opengraph.info_gen(url)# Получаем основную инфу и тело сайта для будущей обработки
    	await message.answer(info, parse_mode="Markdown")# Отправляем сообщение с инфой
    	markup = InlineKeyboardMarkup(row_width=2)# Создаём переменную с каркасом инлайн клавы
    	item1 = InlineKeyboardButton('Да', callback_data='btn1')# Создаём кнопку да
    	item2 = InlineKeyboardButton('Нет', callback_data='btn2')# Создаём кнопку нет
    	item3 = InlineKeyboardButton('Добавить в подписки', callback_data='btn3')
    	markup.add(item1, item2, item3)# К инлайн клаве добавляем две кнопки
    	await message.answer('Хотите получить информацию отдельно по биржам?', reply_markup=markup)# Отправяем сообщение с прикреплённой инлайн клавой
    # Ловим экспекты если пользователю стало скучно
    except MissingSchema:
    	await message.answer('Это не похоже на ссылку')
    except InvalidURL:
    	await message.answer('Хост по данной ссылке не найден')
    except Timeout:
    	await message.answer('Сервер не прислал ответ, возможно он сейчас отключен, или у нас технические неполадки')
    except InvalidSchema:
    	await message.answer('Неправильная ссылка')
    except AttributeError:
    	await message.answer('Ссылка введёт не на myfin, или бот отправлял слишком много запросов и нас заблокировали, попробуйте позже.\n\nТакже возможно сайт был обновлён и на данный момент мы не можем получить данные с него')
    except Exception:
    	await message.answer('Непредвиденная ошибка, проверьте ссылку')


#----------------------- Menu ------------------
@dp.message_handler(commands = ['menu'])
async def menu(message, state: FSMContext):
	markup = InlineKeyboardMarkup(row_width=1)# Создаём переменную с каркасом инлайн клавы
	item1 = InlineKeyboardButton('Избранные', callback_data='btnlist')# Создаём кнопку да
	item2 = InlineKeyboardButton('Отписаться', callback_data='unsub')
	item3 = InlineKeyboardButton('Выйти', callback_data='exit')
	markup.add(item1, item2, item3)
	await message.answer('Меню', reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == 'exit')
async def exit(callback_query: types.CallbackQuery):
	await callback_query.message.delete()
	await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'unsub') 
async def handle_unsub(callback_query: types.CallbackQuery):
	no = ''
	await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="Выберете из списка валюты от которых хотите отписаться\nИ напишите их через пробел", reply_markup=None)
	no = await db_fav.spisok(callback_query.from_user.id)
	if no != 'no':
		await InputUserData.step_1.set()
		await callback_query.answer()
	else:
		await callback_query.answer()

@dp.message_handler(state=InputUserData.step_1, content_types=types.ContentTypes.TEXT)
async def questionnaire_state_1_message(message: types.Message, state: FSMContext):
	async with state.proxy() as user_data:
		user_data['input_user'] = message.text.replace('\n',' ')
		a = user_data['input_user']
		if a == "/cancel":
			await state.finish()
			await menu(message, state)	
		else:
			await db_fav.fav_remove(message.from_user.id, a)
			await state.finish()



#------------------ Каллбек с подробной инфа ---------------------
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))# обьект который отслеживает каллбеки которые начинаются с btn
async def callback_unline(callback_query: types.CallbackQuery):
	code = callback_query.data# В переменную передаём дату каллбека

	if callback_query.data == 'btn1':# Если это бтн1
		await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text='Отправляю информацию', reply_markup=None)# Изменяем текст сообщения и убираем инлайн клаву
		time.sleep(1)
		#print(callback_query.from_user.id)
		await opengraph.info_birjes(db[callback_query.from_user.id], callback_query.from_user.id)# Вызываем функцию для инфы с бирж
	elif callback_query.data == 'btn2':
		await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text='Хорошо', reply_markup=None)# Изменяем текст и убираем клаву
	elif callback_query.data == 'btn3':
		await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text = 'Добавляю', reply_markup=None)
		await db_fav.fav_add(callback_query.from_user.id, db[callback_query.from_user.id])
	elif callback_query.data == 'btnlist':
		await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text = 'Просматриваю ваши подписки', reply_markup=None)
		await db_fav.spisok(callback_query.from_user.id)
	await callback_query.answer()


async def sendsub(wait_for):
	while True:
		await asyncio.sleep(wait_for)
		people = await db_fav.people()
		for i in people:
			urls = i[1].split(";")
			for url in urls:
				info, r = await opengraph.info_gen(url)
				await bot.send_message(i[0], info, parse_mode='Markdown')

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.create_task(sendsub(300))
	executor.start_polling(dp, skip_updates=True)