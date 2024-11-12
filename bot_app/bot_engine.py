"""
Main bot module. Includes bot start and notifications functionality.
"""
import logging
from logging.handlers import RotatingFileHandler
import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageError, PollError
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from arsenic.errors import ArsenicTimeout, ArsenicError
from weather_parser import WeatherParser

load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=storage)

logger = logging.getLogger('bot_log')
rfh = RotatingFileHandler(
    filename='bot_log.log',
    maxBytes=1024,
    backupCount=1,
    delay=False,
)

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",  # Fixed here
    datefmt="%y-%m-%d %H:%M:%S",
    handlers=[
        rfh
    ]
)


class DialogStates(StatesGroup):
    location_verification = State()
    chosen_option = State()
    dialog_started = State()


@dp.message_handler(commands=['start'], state='*')
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
        parser = WeatherParser()
        loc = await parser.check_location(message.text)
        await bot.send_message(message.from_user.id, f'Ваш населенный пункт {loc[0]}?', reply_markup=markup)
        await state.update_data(location=loc[0], url=loc[1])
        await DialogStates.location_verification.set()
    except (MessageError, PollError, ArsenicTimeout,
            ArsenicError, Exception) as e:
        logger.error(e)
        logger.log(logging.ERROR, str(e))
        await bot.send_message(message.from_user.id, 'Извините, не нашли такого населенного пункта 🙁')
        await bot.send_message(message.from_user.id,
                         'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"')


@dp.message_handler(state=DialogStates.location_verification)
async def verify_location(message: types.Message, state: FSMContext):
    remove_buttons = types.ReplyKeyboardRemove()
    user_data = await state.get_data()
    if message.text == 'Да':
        try:
            parser = WeatherParser()
            forecast = await parser.get_forecast(user_data['url'])
            await state.update_data(forecast=forecast)
            await bot.send_message(message.from_user.id, 'Отлично!', reply_markup=remove_buttons)
            await get_forecast_option(message)
        except (MessageError, PollError, ArsenicTimeout,
                ArsenicError, Exception) as e:
            logger.error(e)
            logger.log(logging.ERROR, str(e))
            await bot.send_message(message.from_user.id, 'Извините, не получилось загрузить прогноз погоды 😟')
            await bot.send_message(message.from_user.id, 'Пожалуйста, нажмите на /start', reply_markup=remove_buttons)

    else:
        await bot.send_message(message.from_user.id,
                         'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"', reply_markup=remove_buttons)
        await DialogStates.dialog_started.set()


async def get_forecast_option(message: types.Message):
    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    today = types.InlineKeyboardButton(text='Погода на сегодня', callback_data='0')
    tomorrow = types.InlineKeyboardButton(text='Погода на завтра', callback_data='1')
    five_day_forecast = types.InlineKeyboardButton(text='Погода на 5 дней', callback_data='2')
    markup.add(today)
    markup.add(tomorrow)
    markup.add(five_day_forecast)
    await bot.send_message(message.from_user.id,
                           'Выбери опцию получения прогноза погоды',
                           reply_markup=markup)
    await DialogStates.chosen_option.set()


@dp.callback_query_handler(lambda call: call.data == "0" or call.data == "1" or call.data == "2", state=DialogStates.chosen_option)
async def print_forecast(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    remove_buttons = types.ReplyKeyboardRemove()
    try:
        if callback.data == '0' or callback.data == '1':
            answer = await get_today_or_tomorrow_forecast(user_data, callback.data)
        else:
            first_two_days, answer = await get_five_days_forecast(user_data)
            await bot.send_message(callback.from_user.id, first_two_days)

        await bot.send_message(callback.from_user.id, answer, reply_markup=remove_buttons)
        await bot.send_message(callback.from_user.id,
                               'Если хотитите получить прогноз погоды в другом городе, нажмите /start')
    except (MessageError, PollError, ArsenicTimeout,
            ArsenicError, Exception) as e:
        logger.error(e)
        logger.log(logging.ERROR, str(e))
        await bot.send_message(callback.from_user.id, 'Извините, не получилось загрузить прогноз погоды 😟')
        await bot.send_message(callback.from_user.id, 'Пожалуйста, нажмите на /start')
    finally:
        await state.finish()


async def get_today_or_tomorrow_forecast(forecast_data: dict, callback_data: str) -> str:
    """
    Method to create today or tomorrow forecast answer
    :param callback_data: Callback option that user chose
    :param forecast_data: Forecast data as dict
    :return: forecast as a string
    """
    if callback_data == '0':
        date = list(forecast_data['forecast'])[0]
    else:
        date = list(forecast_data['forecast'])[1]

    daytimes = list(forecast_data['forecast'][date])
    answer = f"""
                {forecast_data['forecast']['city']}

                {date}

                {daytimes[0]}: \n{forecast_data['forecast'][date][daytimes[0]]}

                {daytimes[1]}: \n{forecast_data['forecast'][date][daytimes[1]]}

                {daytimes[2]}: \n{forecast_data['forecast'][date][daytimes[2]]}

                {daytimes[3]}: \n{forecast_data['forecast'][date][daytimes[3]]}
                """
    return answer


async def get_five_days_forecast(forecast_data: dict) -> (str, str):
    """
    Method to create 5-day forecast answer
    :param forecast_data: Forecast data as dict
    :return: tuple of strings with brief forecast info
    """
    two_days_answer = f"{forecast_data['forecast']['city']}\n\n"
    three_days_answer = ""
    first_two_days = list(forecast_data['forecast'])[:2]
    last_three_days = list(forecast_data['forecast'])[2:-1]
    for key in first_two_days:
        temp_forecast = f"{key}\n{await get_forecast_details(forecast_data, key)}\n\n"
        two_days_answer += temp_forecast
    for key in last_three_days:
        temp_forecast = f"{key}\n{await get_forecast_details(forecast_data, key)}\n\n"
        three_days_answer += temp_forecast
    return two_days_answer, three_days_answer


async def get_forecast_details(forecast_dict: dict, data: str) -> str:
    """

    :param data:
    :param forecast_dict:
    :return:
    """
    answer = ""
    for daytime, forecast_info in forecast_dict['forecast'][data].items():
        temp = forecast_info.split('\n')
        info = temp[:2] + [temp[-1]]
        answer += f"""
                   {daytime}: {" ".join(info)}
                   """
    return answer

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
