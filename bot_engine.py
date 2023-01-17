"""
Main bot module. Includes bot start and notifications functionality.
"""
import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from weather_parser import WeatherParser

load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=storage)
parser = WeatherParser()


class DialogStates(StatesGroup):
    location_verification = State()
    chosen_option = State()
    dialog_started = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Bot initialization
    :param message:
    """

    await bot.send_message(message.from_user.id, '👋 Привет! Я бот прогноза погоды. ')
    await bot.send_message(message.from_user.id,
                           'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"')
    await DialogStates.dialog_started.set()


@dp.message_handler(state=DialogStates.dialog_started)
async def get_weather_location(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Да')
    btn2 = types.KeyboardButton('Нет')
    markup.add(btn1, btn2)
    try:
        loc = parser.check_location(message.text)
        await bot.send_message(message.from_user.id, f'Ваш населенный пункт {loc[0]}?', reply_markup=markup)
        await state.update_data(location=loc[0], url=loc[1])
        await DialogStates.location_verification.set()

    except:
        await bot.send_message(message.from_user.id, 'Извините, не нашли такого населенного пункта 🙁')
        await bot.send_message(message.from_user.id,
                         'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"')
        await DialogStates.dialog_started.set()


@dp.message_handler(state=DialogStates.location_verification)
async def verify_location(message: types.Message, state: FSMContext):
    remove_buttons = types.ReplyKeyboardRemove()
    user_data = await state.get_data()
    if message.text == 'Да':
        forecast = parser.get_forecast(user_data['url'])
        await state.update_data(forecast=forecast)
        await bot.send_message(message.from_user.id, 'Отлично!', reply_markup=remove_buttons)
        await get_forecast_option(message)
    else:
        await bot.send_message(message.from_user.id,
                         'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"', reply_markup=remove_buttons)
        await DialogStates.dialog_started.set()


async def get_forecast_option(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    today = types.KeyboardButton(text='Погода на сегодня')
    tomorrow = types.KeyboardButton(text='Погода на завтра')
    markup.add(today, tomorrow)
    await bot.send_message(message.from_user.id,
                           'Выбери опцию получения прогноза погоды',
                           reply_markup=markup)
    await DialogStates.chosen_option.set()


@dp.message_handler(state=DialogStates.chosen_option)
async def print_forecast(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    remove_buttons = types.ReplyKeyboardRemove()
    if message.text == 'Погода на сегодня':
        date = list(user_data['forecast'])[0]
    else:
        date = list(user_data['forecast'])[1]

    daytimes = list(user_data['forecast'][date])
    answer = f"""
        {user_data['forecast']['city']}

        {date}

        {daytimes[0]}: \n{user_data['forecast'][date][daytimes[0]]}

        {daytimes[1]}: \n{user_data['forecast'][date][daytimes[1]]}

        {daytimes[2]}: \n{user_data['forecast'][date][daytimes[2]]}

        {daytimes[3]}: \n{user_data['forecast'][date][daytimes[3]]}
        """

    await bot.send_message(message.from_user.id, answer, reply_markup=remove_buttons)
    await bot.send_message(message.from_user.id,
                           'Если хотитите получить прогноз погоды в другом городе, нажмите /start')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




