import asyncio
import os
import re
import aiofiles
from tqdm.asyncio import tqdm
from playwright.async_api import async_playwright
from markdownify import markdownify as md

BASE_DIR = "Data_Eng_test"
LANGUAGE = "en"
BASE_QUERY_SELECTOR = "div.card.legislation-card.mb-base div.card-body"
TITLE_REGEX = r"[^\w\s\-_]"

def sanitize_name(title):
    return re.sub(TITLE_REGEX, '', title).strip()

async def scrapPageData(url, page):
    try:
        await page.goto(
            url, 
            timeout=60000
            )
        
        await page.wait_for_selector(BASE_QUERY_SELECTOR)
        
        title = await page.inner_html(BASE_QUERY_SELECTOR + " h1.legislation-title")
        # description = await page.inner_html(BASE_QUERY_SELECTOR + " div.details-contant div.row.mb-4")
        
        # print(description)

        content = await page.evaluate('''
            () => {
                const copyBtnGroups = document.querySelectorAll('div.d-flex.align-items-center.copyBtnGroup');
                for(let btn of copyBtnGroups){ 
                    btn.remove();
                }
                
                const parentDiv = document.querySelector('.order-1.order-lg-0.mt-4.mt-lg-0.col-lg-8.col-md-10');
                if (parentDiv) {
                    const childDivs = parentDiv.querySelectorAll('.legislation-content.isParent.is-part');
                    childDivs.forEach(div => {
                        const h3Tags = div.querySelectorAll('h3.title.d-flex.align-items-center');
                        h3Tags.forEach(tag => {
                            // Create a new h2 tag
                            const h2 = document.createElement('h2');
                            h2.className = 'title d-flex align-items-center';
                            h2.textContent = "## " + tag.textContent.trim(); // Only keep the text content
                            // Replace the h3 tag with the new h2 tag
                            tag.replaceWith(h2);
                        });
                    });
                }
                return parentDiv.innerHTML;
            }
        ''')
        
        title = md(title)
        # description = md(description)
        content = md(content)

        return f"URL:{url}\n# {title}\n\n{content}", title, None
    except Exception as e:
        print(f"Error occurred while scraping {url}: {e}")
        return None, None, url 

async def saveMarkdownFile(filename, markdown_content):
    try:
        async with aiofiles.open(filename, "w", encoding="utf-8") as file:
            await file.write(markdown_content)
    except Exception as e:
        print(f"Error occurred while saving {filename}: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        with open("urls.txt", "r", encoding="utf-8") as f:
            urls = f.readlines()
            
        # urls = ["https://laws.moj.gov.sa/legislation/S6ocDdXJDZl1v2FSH0+a3g=="]
        
        success_count = 0
        failed_urls = []
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR)
        for url in tqdm(urls, desc="Processing URLs"):
            url = url.strip() 
            
            if LANGUAGE == "en":
                url = f"{url}?lang=en"
            
            markdown_content, title, failed_url = await scrapPageData(url, page)
            
            if markdown_content is not None:
                title = sanitize_name(title)
                filename = f"{BASE_DIR}/{title}.md"
                print(filename)
                await saveMarkdownFile(filename, markdown_content)
                success_count += 1
            else:
                failed_urls.append(failed_url)

        if failed_urls:
          with open("failed_urls.txt", "w", encoding="utf-8") as f:
              for failed_url in failed_urls:
                  f.write(f"{failed_url}\n")

        print(f"{success_count} pages data scrapped successfully")
        await browser.close()

asyncio.run(main())
