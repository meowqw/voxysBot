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
    
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """START HANDLING"""

    # start fullname state
    await meetingForm.name.set()
    await bot.send_message(message.chat.id, 'Привет, здесь ты можешь записаться на собеседование')
    await bot.send_message(message.chat.id, 'Как тебя зовут')

@dp.message_handler(state=meetingForm.name)
async def process_name(message: types.Message, state: FSMContext):
    """NAME STATE"""

    async with state.proxy() as data:
        data['name'] = message.text

    # start phone state
    await meetingForm.next()
    await bot.send_message(message.chat.id, "Введи свой номер телефона в формате\n8-XXX-XXX-XX-XX")

# проверка маски телефона
@dp.message_handler(lambda message: bool(re.match(r"^8-\d{3}-\d{3}-\d{2}-\d{2}$", message.text)) != True, state=meetingForm.phone)
async def process_phone_invalid(message: types.Message):
    return await message.reply('Не валидный формат, введи в формате 8-XXX-XXX-XX-XX')    


@dp.message_handler(lambda message: bool(re.match(r"^8-\d{3}-\d{3}-\d{2}-\d{2}$", message.text)), state=meetingForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    """PHONE STATE"""

    async with state.proxy() as data:
        data['phone'] = message.text

    # start date state
    await meetingForm.next()
    await bot.send_message(message.chat.id, 'Введи дату в формате ДД.ММ.ГГГГ')
    

# проверка маски даты
@dp.message_handler(lambda message: bool(re.match(r"^\d{2}\.\d{2}\.\d{4}$", message.text)) != True, state=meetingForm.date)
async def process_date_invalid(message: types.Message):
    return await message.reply('Не валидный формат, введи в формате ДД.ММ.ГГГГ') 


@dp.message_handler(lambda message: bool(re.match(r"^\d{2}\.\d{2}\.\d{4}$", message.text)), state=meetingForm.date)
async def process_date(message: types.Message, state: FSMContext):
    """DATE STATE"""

    async with state.proxy() as data:
        data['date'] = message.text

    # start time state
    await meetingForm.next()
    await bot.send_message(message.chat.id, 'Введи время в формате ЧЧ:ММ')

# проверка маски времени
@dp.message_handler(lambda message: bool(re.match(r"^\d{2}\:\d{2}$", message.text)) != True, state=meetingForm.time)
async def process_time_invalid(message: types.Message):
    return await message.reply('Не валидный формат, введи в формате ЧЧ:ММ') 

@dp.message_handler(lambda message: bool(re.match(r"^\d{2}\:\d{2}$", message.text)), state=meetingForm.time)
async def process_time(message: types.Message, state: FSMContext):
    """TIME STATE"""

    async with state.proxy() as data:
        data['time'] = message.text
        
    client_id = post_client({'name': data['name'], 'phone': data['phone']})
    if client_id:
        meeting = post_meeting({'date': data['date'], 'time': data['time'], 'client_id': client_id})
        
        if meeting:

            await bot.send_message(
                    message.chat.id,
                    md.text(
                        md.text('Спасибо за проявленный интерес к нашей компании', md.bold(data['name'])),
                        md.text('Телефон: ', data['phone']),
                        md.text('Дата записи: ', data['date']),
                        md.text('Время записи: ', data['time']),
                        md.text(
                            md.bold('В день собеседования, за пол часа до начала, пришлю уведомление')),
                        sep='\n',
                    ),
                    parse_mode=ParseMode.MARKDOWN,
            )
        else: 
             await bot.send_message(message.chat.id, 'Что то пошло не так, попробуйте еще раз введя /start')
    
    await state.finish()
        
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)