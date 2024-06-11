import os
import re
import asyncio
import aiohttp
import aiofiles
import urllib.parse
import json
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm

PDF_BASE_URL = "https://apis.moj.gov.sa/lawsreg/apis/legislations/v1/export-statute/full/pdf?Serial="
BASE_FILE_PATH = "Data"

async def get_html(session, url):
    async with session.get(url) as response:
        return await response.text()

def extract_title(soup_html):
    title_tag = soup_html.find('h1', class_='legislation-title')
    return title_tag.get_text(strip=True) if title_tag else None

def extract_serial(soup_html):
    for script in soup_html.find_all('script'):
        if script.string:
            match = re.search(r'serial:\s*"(.*?)"', script.string)
            if match:
                serial = match.group(1).encode().decode('unicode_escape')
                return urllib.parse.quote(serial, safe='')
    return None

async def get_pdf_url_title(session, url):
    html_content = await get_html(session, url)
    soup_html = BeautifulSoup(html_content, 'html.parser')
    title = extract_title(soup_html)
    serial = extract_serial(soup_html)
    return PDF_BASE_URL + serial, title

async def download_pdf(session, pdf_url, file_name):
    async with session.get(pdf_url) as response:
        if response.status == 200:
            async with aiofiles.open(file_name, 'wb') as f:
                await f.write(await response.read())
            return True
        return False

async def process_url(session, url, defected_urls):
    pdf_url, title = await get_pdf_url_title(session, url)
    if pdf_url and title:
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        file_name = os.path.join(BASE_FILE_PATH, f"{sanitized_title}.pdf")
        if not await download_pdf(session, pdf_url, file_name):
            defected_urls[url] = pdf_url
    else:
        defected_urls[url] = None

async def main():
    if not os.path.exists(BASE_FILE_PATH):
        os.makedirs(BASE_FILE_PATH)

    async with aiohttp.ClientSession() as session:
        with open("./urls.txt", 'r') as file:
            urls = [url.strip() for url in file.readlines()]

        defected_urls = {}

        for url in tqdm(urls, desc="Processing URLs"):
            await process_url(session, url, defected_urls)

        with open("defects.json", 'w') as f:
            json.dump(defected_urls, f)

if __name__ == "__main__":
    asyncio.run(main())
