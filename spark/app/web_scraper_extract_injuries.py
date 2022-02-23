import time
import os
from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp

INJURIES_DATA_URL = os.getenv("INJURIES_DATA_URL")


def get_page_content(URL: str) -> bytes:
    html = requests.get(URL).content
    return html


def get_schema(url: str) -> list:
    html = get_page_content(url)
    soup = BeautifulSoup(html, 'lxml')
    col_names = map(lambda x: x.text, soup.select('th'))
    return list(col_names)


def scrap_urls_and_flags(url: str) -> list:
    html = get_page_content(url)
    soup = BeautifulSoup(html, 'lxml')
    url_pattern = "https://hashtagbasketball.com{}"
    urls = list(map(lambda x: (url_pattern.format(x['href']), x.text), soup.select('td a')))
    return urls


async def get_page(url: str, session: aiohttp.ClientSession) -> str:
    async with session.get(url=url) as response:
        html = await response.text()
        return html


def filter_data(data_record: list) -> list:
    return list(map(lambda x: x.select_one('span.visible-xs').text if x.find('span') else x.text, data_record))


async def get_data(url: str, session: aiohttp.ClientSession) -> list:
    html = await get_page(url, session)
    soup = BeautifulSoup(html, 'lxml')
    records = list(filter(lambda x: x.find('td'), soup.select('tr')))
    data = list(map(lambda x: x.select('td'), records))
    filtered_data = list(map(lambda x: filter_data(x), data))
    return filtered_data


async def main_crawler(urls: list):
    async with aiohttp.ClientSession() as session:
        tasks = [get_data(url[0], session) for url in urls]
        data = await asyncio.gather(*tasks)
        return data





