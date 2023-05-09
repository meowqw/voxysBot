from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import config
from aiogram.types import ParseMode
from aiogram.utils.markdown import link
import logging
import aiogram.utils.markdown as md
import datetime
import re
from api import *


bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# form meetingForm


class meetingForm(StatesGroup):
    name = State()
    phone = State()
    date = State()
    time = State()


# main keyboard
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row('Записаться 📝',
                  'Информация 📖')


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """START HANDLING"""

    await bot.send_message(message.chat.id,
                           'Привет 👋, здесь ты можешь получить информацию о компании и вакансиях и записаться на собеседование',
                           reply_markup=main_keyboard)


@dp.message_handler(Text(equals='Записаться 📝'))
async def function_sign_up(message: types.Message):
    """Отработка нажатия ЗАПИСАТЬСЯ"""

    # start fullname state
    await meetingForm.name.set()
    await bot.send_message(message.chat.id, 'Как тебя зовут')
    
    
@dp.message_handler(Text(equals='Информация 📖'))
async def function_information(message: types.Message):
    """Отработка нажатия ИНФОРМАЦИЯ"""

    information = get_information()
    if information:
        for item in information:
            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text(md.bold(item['title'])),
                    md.text(item['text']),
                    sep='\n',
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
            
    else:
        await bot.send_message(message.chat.id, 'Что то пошло не так, попробуйте еще раз 🥺')


@dp.message_handler(state=meetingForm.name)
async def process_name(message: types.Message, state: FSMContext):
    """NAME STATE"""

    async with state.proxy() as data:
        data['name'] = message.text

    # start phone state
    await meetingForm.next()
    await bot.send_message(message.chat.id, "☎️ Введи свой номер телефона в формате\n8-XXX-XXX-XX-XX")

# проверка маски телефона


@dp.message_handler(lambda message: bool(re.match(r"^8-\d{3}-\d{3}-\d{2}-\d{2}$", message.text)) != True, state=meetingForm.phone)
async def process_phone_invalid(message: types.Message):
    return await message.reply('❌ Не валидный формат, введи в формате 8-XXX-XXX-XX-XX')


def render_date_buttons():
    date_keyboard = types.InlineKeyboardMarkup(
        resize_keyboard=True, selective=True)


    date_btn_today = types.InlineKeyboardButton(
        'Сегодня', callback_data='date_btn_today')
    date_btn_tomorrow = types.InlineKeyboardButton(
        'Завтра', callback_data='date_btn_tomorrow')
    date_btn_day_after_tomorrow = types.InlineKeyboardButton(
        'Послезавтра', callback_data='date_btn_day_after_tomorrow')
    date_keyboard.add(date_btn_today, date_btn_tomorrow, date_btn_day_after_tomorrow)
    
    return date_keyboard


@dp.message_handler(lambda message: bool(re.match(r"^8-\d{3}-\d{3}-\d{2}-\d{2}$", message.text)), state=meetingForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    """PHONE STATE"""

    async with state.proxy() as data:
        data['phone'] = message.text

    # start date state
    await meetingForm.next()
    await bot.send_message(message.chat.id, '📅 Выбери удобную дату', reply_markup=render_date_buttons())



def render_time_buttons():
    time_keyboard = types.InlineKeyboardMarkup(
        resize_keyboard=True, selective=True)


    time_btn_one = types.InlineKeyboardButton(
        '12:00', callback_data='time_btn_12:00')
    time_btn_two = types.InlineKeyboardButton(
        '15:00', callback_data='time_btn_15:00')
    time_btn_three = types.InlineKeyboardButton(
        '18:00', callback_data='time_btn_18:00')
    time_keyboard.add(time_btn_one, time_btn_two, time_btn_three)
    
    return time_keyboard


@dp.callback_query_handler(Text(startswith="date_btn_"), state=meetingForm.date)
async def callbacks_process_date(call: types.CallbackQuery, state: FSMContext):
    """CALLBACK DATE"""
    action = call.data.split('date_btn_')[1]

    if action == "today":
        date = datetime.datetime.today().date()
    elif action == 'tomorrow':
        date = (datetime.datetime.today() + datetime.timedelta(days=1)).date()
    elif action == 'day_after_tomorrow':
        date = (datetime.datetime.today() + datetime.timedelta(days=2)).date()
        
    async with state.proxy() as data:
        data['date'] = date
    
    await meetingForm.next()
    await bot.send_message(call.message.chat.id, '🕐 Выбери удобное время', reply_markup=render_time_buttons())
        

@dp.callback_query_handler(Text(startswith="time_btn_"), state=meetingForm.time)
async def callbacks_process_time(call: types.CallbackQuery, state: FSMContext):
    """CALLBACK TIME"""
    action = call.data.split('time_btn_')[1]
        
    async with state.proxy() as data:
        data['time'] = action
        
    client_id = post_client({'name': data['name'], 'phone': data['phone']})
    print(client_id)
    if client_id:
       
        meeting = post_meeting(
            {'date': data['date'], 'time': data['time'], 'client_id': client_id})
        
        print(meeting)

        if meeting:

            await bot.send_message(
                call.message.chat.id,
                md.text(
                    md.text('Спасибо за проявленный интерес к нашей компании ☺️', md.bold(
                            data['name'])),
                    md.text('Телефон: ', data['phone']),
                    md.text('Дата записи: ', data['date']),
                    md.text('Время записи: ', data['time']),
                    md.text(
                        md.bold('В день собеседования, за пол часа до начала, пришлю уведомление 🔔')),
                    sep='\n',
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await bot.send_message(call.message.chat.id, 'Что то пошло не так, попробуйте еще раз 🥺')

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
