"""
Parser to get weather forecast from Yandex.Weather
"""

from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

from arsenic import get_session, keys, browsers, services

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
        t = ChromeDriverManager().install()
        self._service = services.Chromedriver(binary=t)
        self._browser = browsers.Chrome()

        self._browser.capabilities = {
            "goog:chromeOptions": {"args": [
                '--headless',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080',
            ]
            }
        }

    async def check_location(self, location: str):
        default_url = 'https://dzen.ru/pogoda/'
        async with get_session(self._service, self._browser) as session:
            await session.get(default_url)
            search = await session.wait_for_element(15, 'input.mini-suggest-form__input.mini-suggest__input')
            await search.send_keys(location)
            await search.send_keys(keys.ENTER)
            search_results = await session.wait_for_element(15, 'a.link.place-list__item-name')
            url = await search_results.get_attribute('href')
            text = await search_results.get_text()
            return text, f'https://dzen.ru{url}'

    async def get_forecast(self, url):
        result = {}
        async with get_session(self._service, self._browser) as session:
            await session.get(url)
            await session.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            await session.wait_for_element(15, 'div.forecast-details__day-info')
            forecast = await session.get_page_source()
            soup = BeautifulSoup(forecast, 'lxml')
            five_days = soup.find_all('div', {'class': 'forecast-details__day-info'})[:2]
            for day in five_days:
                details = day.find_all('tr', {'class': 'weather-table__row'})
                date = day.find_previous_sibling('div', {'class': 'forecast-details__day'})
                date_description = date.find('div', {'class': 'a11y-hidden'}).text
                result[date_description] = {}
                for detail in details:
                    temperature: str = detail.find('div', {'class': 'a11y-hidden'}).text
                    condition: str = detail.find('td', {
                        'class': 'weather-table__body-cell weather-table__body-cell_type_condition'}).text
                    pressure: str = detail.find('td', {
                        'class': 'weather-table__body-cell weather-table__body-cell_type_air-pressure'}).text
                    humidity: str = detail.find('td', {
                        'class': 'weather-table__body-cell weather-table__body-cell_type_humidity'}).text
                    wind_speed: str = detail.find('span', {'class': 'wind-speed'}).text
                    wind_direction: str = detail.find('div', {'class': 'weather-table__wind-direction'}).text
                    result[date_description][
                        temperature[
                        :temperature.index(',')].title()] = f"🌡 {temperature[temperature.index(',') + 2:]},\n" \
                                                            f"{condition} {EMOJI_WEATHER_DICT.get(condition, '')},\n" \
                                                            f"Давление: {pressure} мм рт. ст.,\n" \
                                                            f"Влажность 💦: {humidity},\n" \
                                                            f"Ветер 🌬: {wind_speed} м/с {wind_direction}"

            city = soup.find('h1', {'class': 'title title_level_1 header-title__title'}).text
            result['city'] = city
            return result
