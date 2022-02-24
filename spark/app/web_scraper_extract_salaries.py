import time
import os
from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

BASEDIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASEDIR / ".env")

SALARIES_DATA_URL = os.getenv("SALARIES_DATA_URL")


def get_page_content(URL: str) -> bytes:
    html = requests.get(URL).content
    return html


def get_schema(url: str) -> list:
    html = get_page_content(url)
    soup = BeautifulSoup(html, 'lxml')
    func = lambda x: x.text.strip() if x.text.strip() != "" else "Rank"
    col_names = map(lambda x: func(x), soup.select('thead td'))
    return list(col_names)


def scrap_urls_and_flags(url: str) -> list:
    html = get_page_content(url)
    soup = BeautifulSoup(html, 'lxml')
    a_tags = soup.select('li.all a')
    urls = [(el["href"], el.text.strip()) for el in a_tags if int(el.text.strip().split("/")[0]) >= 2000]
    return urls


async def get_page(url: str, session: aiohttp.ClientSession) -> str:
    async with session.get(url=url) as response:
        html = await response.text()
        return html


async def get_data(url: str, session: aiohttp.ClientSession) -> list:
    html = await get_page(url, session)
    soup = BeautifulSoup(html, 'lxml')
    records = soup.select('tbody tr')
    func = lambda x: [el.text.strip() for el in x if el.text.strip()]
    data = map(lambda x: func(x), records)
    return list(data)


async def main_crawler(urls: list):
    async with aiohttp.ClientSession() as session:
        tasks = [get_data(url[0], session) for url in urls]
        data = await asyncio.gather(*tasks)
        return data


