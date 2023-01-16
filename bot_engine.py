"""
Main bot module. Includes bot start and notifications functionality.
"""
import os

from dotenv import load_dotenv
import telebot
from telebot import types

from weather_parser import WeatherParser

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
parser = WeatherParser()

forecast, location = None, None


@bot.message_handler(commands=['start'])
def start(message):
    """
    Bot initialization
    :param message:
    """
    bot.send_message(message.from_user.id, '👋 Привет! Я бот прогноза погоды. ')
    bot.send_message(message.from_user.id,
                     'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"')
    bot.register_next_step_handler(message, get_weather_location)


def get_weather_location(message):
    global forecast, location
    forecast, location = None, None
    location = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Да')
    btn2 = types.KeyboardButton('Нет')
    markup.add(btn1, btn2)
    try:
        loc = parser.check_location(message.text)
        bot.send_message(message.from_user.id, f'Ваш населенный пункт {loc}?', reply_markup=markup)
        bot.register_next_step_handler(message, verify_location)

    except:
        bot.send_message(message.from_user.id, 'Извините, не нашли такого населенного пункта 🙁')
        bot.send_message(message.from_user.id,
                         'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"')
        bot.register_next_step_handler(message, get_weather_location)


def verify_location(message):
    remove_buttons = types.ReplyKeyboardRemove()
    if message.text == 'Да':
        global forecast, location
        forecast = parser.get_forecast()
        bot.send_message(message.from_user.id, 'Отлично!', reply_markup=remove_buttons)
        get_forecast_option(message)

    else:
        bot.send_message(message.from_user.id,
                         'Напиши город для поиска прогноза, например "Лондон" или "Комсомольск-на-Амуре"', reply_markup=remove_buttons)
        bot.register_next_step_handler(message, get_weather_location)


def get_forecast_option(message):
    markup = types.InlineKeyboardMarkup()
    today = types.InlineKeyboardButton(text='Погода на сегодня', callback_data='0')
    tomorrow = types.InlineKeyboardButton(text='Погода на завтра', callback_data='1')
    markup.add(today)
    markup.add(tomorrow)
    bot.send_message(message.from_user.id,
                    'Выбери опцию получения прогноза погоды',
                    reply_markup=markup)


@bot.callback_query_handler(lambda q: q.data == '0')
def print_today_forecast(callback_query):
    global forecast
    today = list(forecast)[0]
    print_forecast(callback_query, today)


@bot.callback_query_handler(lambda q: q.data == '1')
def print_tomorrow_forecast(callback_query):
    global forecast
    tomorrow = list(forecast)[1]
    print_forecast(callback_query, tomorrow)


def print_forecast(callback_query, date):
    daytimes = list(forecast[date])
    bot.answer_callback_query(callback_query_id=callback_query.id)
    message = f"""
    {forecast['city']}
    
    {date}
    
    {daytimes[0]}: \n{forecast[date][daytimes[0]]}
    
    {daytimes[1]}: \n{forecast[date][daytimes[1]]}
    
    {daytimes[2]}: \n{forecast[date][daytimes[2]]}
    
    {daytimes[3]}: \n{forecast[date][daytimes[3]]}
    """
    bot.send_message(callback_query.from_user.id, message)
    bot.send_message(callback_query.from_user.id, 'Если хотитите получить прогноз погоды в другом городе, нажмите /start')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)




