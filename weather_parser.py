"""
Parser to get weather forecast from Yandex.Weather
"""
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

EMOJI_WEATHER_DICT = {
    'Ясно': '☀',
    'Малооблачно': '🌤',
    'Облачно с прояснениями': '🌥',
    'Пасмурно': '☁',
    'Небольшой дождь': '🌦',
    'Дождь': '🌧',
    'Снег': '🌨'
}


class WeatherParser:

    def __init__(self) -> None:
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("enable-automation")

        self._browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                         options=options)

    def check_location(self, location: str):
        default_url = 'https://dzen.ru/pogoda'
        self._browser.get(default_url)
        search = self._browser.find_element(by=By.CSS_SELECTOR, value='input.mini-suggest-form__input.mini-suggest__input')
        search.send_keys(location + Keys.RETURN)
        search_results = self._browser.find_element(by=By.CSS_SELECTOR, value='a.link.place-list__item-name')
        url = search_results.get_attribute('href')
        return search_results.text, url


    def get_forecast(self, url):
        result = {}
        self._browser.get(url)
        self._browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        forecast = self._browser.page_source
        soup = BeautifulSoup(forecast, 'lxml')
        five_days = soup.find_all('div', {'class': 'forecast-details__day-info'})[:5]
        for day in five_days:
            details = day.find_all('tr', {'class': 'weather-table__row'})
            date = day.find_previous_sibling('div', {'class': 'forecast-details__day'})
            date_description = date.find('div', {'class': 'a11y-hidden'}).text
            result[date_description] = {}
            for detail in details:
                temperature: str = detail.find('div', {'class': 'a11y-hidden'}).text
                condition: str = detail.find('td', {'class': 'weather-table__body-cell weather-table__body-cell_type_condition'}).text
                pressure: str = detail.find('td', {'class': 'weather-table__body-cell weather-table__body-cell_type_air-pressure'}).text
                humidity: str = detail.find('td', {'class': 'weather-table__body-cell weather-table__body-cell_type_humidity'}).text
                wind_speed: str = detail.find('span', {'class': 'wind-speed'}).text
                wind_direction: str = detail.find('div', {'class': 'weather-table__wind-direction'}).text
                result[date_description][temperature[:temperature.index(',')].title()] = f"🌡 {temperature[temperature.index(',') + 2:]},\n" \
                                                                                         f"{condition} {EMOJI_WEATHER_DICT.get(condition)},\n" \
                                                                                         f"Давление: {pressure} мм рт. ст.,\n" \
                                                                                         f"Влажность 💦: {humidity},\n" \
                                                                                         f"Ветер 🌬: {wind_speed} м/с {wind_direction}"

        city = soup.find('h1', {'class': 'title title_level_1 header-title__title'}).text
        result['city'] = city
        return result

