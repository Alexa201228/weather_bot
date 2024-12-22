"""
Parser to get weather forecast from Yandex.Weather
"""

import logging
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO
)

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
        pass

    async def check_location(self, location: str):
        default_url = 'https://dzen.ru/pogoda/'
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # Set headless=True to run in background
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(default_url)
            input_class = "input.mini-suggest-form__input.mini-suggest__input"
            await page.wait_for_selector(input_class)
            await page.fill(input_class, location)
            await page.press(input_class, "Enter")
            found_location = "a.link.place-list__item-name"
            await page.wait_for_selector(found_location)
            url = await page.get_attribute(found_location, 'href')
            text = await page.inner_text(found_location)
            logging.info(f"{url}, {text}")
            await browser.close()
            return text, f'https://dzen.ru{url}'

    async def get_forecast(self, url):
        result = {}
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)  # Set headless=True to run in background
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(url)

                # Scroll to the bottom of the page
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_selector('article', state='attached')  # Wait until at least one element is attached to the DOM

                # You can wait for all matching elements (if there are multiple)
                await page.locator('article').all()
                forecast = await page.content()
                await browser.close()
            soup = BeautifulSoup(forecast, 'html.parser')
            five_days = soup.find_all("article", {'class': 'card'})[:5]
            filtered_segment_containers = [
                container for container in five_days if not 'card_without-card-decoration' in container.get('class', [])
]
            for day in filtered_segment_containers:
                details = day.find_all('tr', {'class': 'weather-table__row'})
                date = day.find_all('h2', {'class': 'forecast-details__title'})[0]
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

        except Exception as e:
            logging.error(e)
            raise e
