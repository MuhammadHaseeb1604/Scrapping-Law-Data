import asyncio
from tqdm.asyncio import tqdm
from playwright.async_api import async_playwright

async def scrap_page_url(page_url, page):
    try:
        await page.goto(page_url)
        await page.wait_for_selector('div.container-xxl.pt-4 div.row div.col-xl-3.col-lg-4.col-md-6.mb-4')
        cards = await page.query_selector_all('div.container-xxl.pt-4 div.row div.col-xl-3.col-lg-4.col-md-6.mb-4')

        print(len(cards))
        urls = []
        for card in cards:
            url = await card.evaluate('(element) => element.querySelector("a.details.d-flex.text-dark").href')
            urls.append(url)

        return urls
    except Exception as e:
        print(f"Error scraping {page_url}: {e}")
        return []

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        pages = [
            "https://laws.moj.gov.sa/legislations-regulations?pageNumber=1&sortingBy=1&type=1",
            "https://laws.moj.gov.sa/legislations-regulations?pageNumber=2&sortingBy=1&type=1",
            "https://laws.moj.gov.sa/legislations-regulations?pageNumber=3&sortingBy=1&type=1",
            "https://laws.moj.gov.sa/legislations-regulations?pageNumber=4&sortingBy=1&type=1",
            "https://laws.moj.gov.sa/legislations-regulations?pageNumber=5&sortingBy=1&type=1",
        ]

        all_urls = []
        for page_url in pages:
            urls = await scrap_page_url(page_url, page)
            all_urls.extend(urls)

        await browser.close()

        with open('urls.txt', 'a') as f:
            for url in tqdm(all_urls, desc='Writing URLs to file'):
                f.write(url + '\n')

asyncio.run(main())
