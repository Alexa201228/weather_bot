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

forecast = None


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
    global forecast
    parser = WeatherParser(message.text)
    forecast = parser.get_forecast()
    get_forecast_option(message)


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
    {date}
    
    {daytimes[0]}: {forecast[date][daytimes[0]]}
    
    {daytimes[1]}: {forecast[date][daytimes[1]]}
    
    {daytimes[2]}: {forecast[date][daytimes[2]]}
    
    {daytimes[3]}: {forecast[date][daytimes[3]]}
    """
    bot.send_message(callback_query.from_user.id, message)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)




