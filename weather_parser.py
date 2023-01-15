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
    'Ясно': {'Утром': '☀',
             'Днём': '☀',
             'Вечером': '',
             'Ночью': ''},

    'Малооблачно': {'Утром': '☀',
                    'Днём': '☀',
                    'Вечером': '',
                    'Ночью': ''},

    'Облачно с прояснениями': {'Утром': '☀',
                               'Днём': '☀',
                               'Вечером': '',
                               'Ночью': ''},

    'Пасмурно': {'Утром': '☀',
                 'Днём': '☀',
                 'Вечером': '',
                 'Ночью': ''},

}


class WeatherParser:

    def __init__(self, location: str) -> None:
        self._location = location
        options = Options()
        options.add_argument("--headless")
        self._browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                         chrome_options=options)

    def get_forecast(self):
        result = {}
        default_url = 'https://dzen.ru/pogoda/london'
        self._browser.get(default_url)
        search = self._browser.find_element(by=By.CSS_SELECTOR, value='input.mini-suggest-form__input.mini-suggest__input')
        search.send_keys(self._location + Keys.RETURN)
        search_results = self._browser.find_element(by=By.CSS_SELECTOR, value='a.link.place-list__item-name')
        search_results.click()
        self._browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(1)
        forecast = self._browser.page_source
        soup = BeautifulSoup(forecast, 'lxml')
        two_days = soup.find_all('div', {'class': 'forecast-details__day-info'})[:2]
        for day in two_days:
            details = day.find_all('tr', {'class': 'weather-table__row'})
            date = day.find_previous_sibling('div', {'class': 'forecast-details__day'})
            date_description = date.find('div', {'class': 'a11y-hidden'}).text
            result[date_description] = {}
            for detail in details:
                temperature: str = detail.find('div', {'class': 'a11y-hidden'}).text
                condition: str = detail.find('td', {'class': 'weather-table__body-cell weather-table__body-cell_type_condition'}).text
                result[date_description][temperature[:temperature.index(',')].title()] = f"{temperature[temperature.index(',') + 2:]}, {condition}"

        return result

