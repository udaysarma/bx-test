from browser import get_browser_page
from oxylabs.proxy import get_proxy_given_country
from helpers.forms import FormParser
from helpers.llm_functions import is_search_form
from helpers.products import ProductParser
import asyncio
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlencode, urlparse
from typing import List, Dict, Any, Optional
import redis
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def parse_forms_from_html(html_content, base_url=None):
    """
    Parse HTML content and extract form details including input names, action, and method
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    forms_data = []
    
    # Find all forms
    forms = soup.find_all('form')
    
    for i, form in enumerate(forms):
        form_info = {
            'form_index': i + 1,
            'action': form.get('action', ''),
            'method': form.get('method', 'GET').upper(),
            'id': form.get('id', ''),
            'class': form.get('class', []),
            'inputs': []
        }
        
        # Make action URL absolute if base_url provided
        if base_url and form_info['action']:
            form_info['action'] = urljoin(base_url, form_info['action'])
        
        # Find all form elements (input, select, textarea)
        form_elements = form.find_all(['input', 'textarea'])
        
        for element in form_elements:
            element_info = {
                'tag': element.name,
                'name': element.get('name', ''),
                'type': element.get('type', ''),
                'value': element.get('value', ''),
                'id': element.get('id', ''),
                'required': element.has_attr('required'),
                'placeholder': element.get('placeholder', '')
            }
            
            form_info['inputs'].append(element_info)
        
        forms_data.append(form_info)
    
    return forms_data


class BrowserTask:
    def __init__(self, country: str):
        self.proxy = get_proxy_given_country(country)
        self.browser = None
        self.page = None
        self.browser_process = None
    
    async def _init(self):
        self.browser, self.page = await get_browser_page(self.proxy)
        if hasattr(self.browser, 'process'):
            self.browser_process = self.browser.process

    async def get_html(self, url):
        if not self.browser:
            await self._init()
        if not self.page:
            try:
                await self.browser.close()
            except Exception as e:
                print(e)
                return None
            finally:
                await self._init()

        try:
            print(f"Navigating to {url}")
            await self.page.goto(url, {"waitUntil": "networkidle2", "timeout": 60000})
            print(f"Navigated to {url}")
            html = await self.page.content()
            print(f"HTML fetched for {url}")
            f = open(f'{urlparse(url).netloc}.search_results.html', 'w')
            f.write(html)
            f.close()
            return html
        except Exception as e:
            print(e)
            return None

    async def get_navigation_url(self, url, country):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        search_url = redis_client.get(f"{domain}:{country}:search_url")

        if search_url:
            return search_url.decode('utf-8')

        try:
            html = await self.get_html(url)
            if not html:
                return None
            
            forms = parse_forms_from_html(html)
            print(forms)

            def fuckup_url(url: str):
                return url[:-1] if url.endswith('/') else url
            
            def get_action_path(action: str):
                if not action.startswith('http'):
                    return action
                if action.startswith('http'):
                    parsed = urlparse(action)
                    return parsed.path

            search_urls = []

            for form in forms:
                if 'search' not in json.dumps(form).lower():
                    continue
                for input in form['inputs']:
                    if (input['type'] == 'text' or input['type'] == 'search') and ('search' in json.dumps(input).lower() or len(form['inputs']) == 1):
                        search_url = f"{fuckup_url(url)}{get_action_path(form['action'])}?{input['name']}=iphone"
                        search_urls.append(search_url)
                        print(search_url)

            if len(search_urls) > 0:
                redis_client.set(f"{domain}:{country}:search_url", search_urls[0])
                return search_urls[0]
            else:
                return None
        except Exception as e:
            try:
                await self.page.screenshot({'path': 'screenshot.png'})
            except Exception as e:
                pass
            print(e)
            return None

    async def get_products_from_html(self, url):
        html = await self.get_html(url)
        if not html:
            return None
        products_parser = ProductParser(html)
        products = products_parser.parse_all_links_from_html(html)

        from locale import currency
        from urllib.parse import urlparse
        from pydantic import BaseModel
        from typing import List

        class Product(BaseModel):
            index: int
            href: str
            css_path: List[str]
            path: str
            max_common: str

        def get_raw_link(href: str) -> str:
            return urlparse(href).netloc + urlparse(href).path


        current_url = url


        def if_external_link(href: str, current_url: str) -> bool:
            if href.startswith('http'):
                return urlparse(href).netloc != urlparse(current_url).netloc
            if href.startswith('/'):
                return False
            if urlparse('https://' + href).netloc != urlparse(current_url).netloc:
                return True
            return False


        products_split: list[Product] = [
            Product(index=idx, href=get_raw_link(p['href']), css_path=p['css_path'].split(' > '), path=p['css_path'], max_common='')
            for idx,p in enumerate(products)
            if p['href'] and not if_external_link(p['href'], current_url)
        ]

        print("products_split", len(products_split))

        grouped = {}

        for p in products_split:
            if p.href not in grouped:
                grouped[p.href] = []
            grouped[p.href].append(p)

        print("grouped", len(grouped))

        def get_most_common_parent(v):
            min_length = min([len(p.css_path) for p in v])

            if len(set([p.css_path[0] for p in v])) > 1:
                return None

            for i in range(0, min_length):
                if len(set([p.css_path[i] for p in v])) > 1:
                    return Product(
                        index=v[0].index,
                        href=v[0].href,
                        css_path=v[0].css_path[:i],
                        path=' > '.join(v[0].css_path[:i]),
                        max_common=''
                    )
            return None

        candidates = []

        for v in grouped.values():
            if len(v) == 1:
                candidates.append(v[0])
            else:
                parent = get_most_common_parent(v)
                if parent:
                    candidates.append(parent)
                else:
                    candidates += v

        print("candidates", len(candidates))

        for candidate in candidates:
            await self.page.addStyleTag(content=f'''
                {" > ".join(candidate.css_path)} {{
                    border: 2px solid red !important;
                }}
            ''')
            await self.page.waitFor(500)

        print(products_split)
        print(candidates)
        return products

    async def load_page_and_execute(self, url, country):
        if not self.browser:
            await self._init()
        if not self.page:
            try:
                await self.browser.close()
            except Exception as e:
                print(e)
                return None
            finally:
                await self._init()

        await self.page.goto(url, {"waitUntil": "networkidle2", "timeout": 60000})
        print(f"Navigated to {url}")
        html = await self.page.content()
        form_parser = FormParser(html)
        forms = form_parser.parse_forms_from_html(html)
        if len(forms) == 0:
            print(f"No forms found for {url}")
            return
        for form in forms:
            if is_search_form(form_parser.strip_css_paths(form)):
                for idx, input in enumerate(form['inputs']): 
                    css_selector = input['css_path']
                    await self.page.addStyleTag(content=f'''
                        {css_selector} {{
                            border: 2px solid red !important;
                        }}
                    ''')
                    
        await self.page.screenshot({'path': f'{urlparse(url).netloc}.png'})
        await self.page.waitFor(5000)

    async def cleanup(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.page:
            self.page = None

        if self.browser_process and self.browser_process.poll() is None:
            try:
                self.browser_process.terminate()
                # Wait a bit for graceful termination
                await asyncio.sleep(1)
                if self.browser_process.poll() is None:
                    self.browser_process.kill()
            except Exception as e:
                print(f"Error killing browser process: {e}")


async def search_query(url: str, css_path: str, q: str) -> str:
    print(f"Starting search query on URL: {url} with CSS path: {css_path} and query: {q}")
    proxy = get_proxy_given_country('in')
    browser, page = await get_browser_page(proxy)
    await page.goto(url, {"waitUntil": "networkidle2"})
    # await page.waitFor(200 * 1000)
    # Wait for the page to load completely
    await page.waitForSelector('input[type="text"], input[type="search"]', {'visible': True})

    print(f"Page loaded: {url}")
    inputs = await page.evaluate(input_eval_js)
    for i, field in enumerate(inputs, 1):
        print(f"[{i}] {field}")

    print('a')
    print(inputs)
    print('b')

    await page.waitForSelector(css_path, {'visible': True})

    elements = await page.querySelectorAll(css_path)
    print(f"Found {len(elements)} elements")

    value = await page.evaluate(f'''() => {{
        const el = document.querySelector("{css_path}");
        return el ? el.value : null;
    }}''')

    print(f"Value in input field before typing: {value}")

    await page.focus(css_path)  # Focus on the input field using the provided CSS path
    await page.click(css_path)
    await page.keyboard.type(q, delay=10)  # Type the query with a slight delay for realism

    value = await page.evaluate(f'''() => {{
        const el = document.querySelector("{css_path}");
        return el ? el.value : null;
    }}''')

    print(f"Value in input field: {value}")

    # await page.keyboard.press('Enter')

    # for i in range(30):
    #     print(f"Waiting for 1 second... {i+1}", page.url)
    #     await asyncio.sleep(1)

    # Press Enter
    await asyncio.gather(
        page.keyboard.press('Enter'),
        page.waitForNavigation({"waitUntil": "networkidle2"})  # Wait for navigation to complete
    )

    print(page.url)
    content = await page.content()
    print("Content fetched after search")
    await browser.close()
    print("Browser closed")
    return content


async def run_browser_tasks():
    task_browser = BrowserTask("in")
    

    # websites = ['https://www.moglix.com', 'https://www.reliancedigital.in', 'https://play.google.com', 'https://www.smartprix.com', 'https://www.swiggy.com', 'https://www.flipkart.com', 'https://blinkit.com', 'https://www.bigbasket.com', 'https://www.91mobiles.com', 'https://www.poorvika.com', 'https://www.zeptonow.com', 'https://dir.indiamart.com', 'https://www.ajio.com', 'https://www.myntra.com', 'https://www.vijaysales.com', 'https://m.snapdeal.com', 'https://www.croma.com', 'https://www.nykaafashion.com']
    # websites = ['https://www.jiomart.com']

    websites = ['https://www.flipkart.com/search?q=iphone%2016%20max%20pro']
    # Sequential execution
    for url in websites:
        await task_browser.get_products_from_html(url)
    
    await task_browser.cleanup()

if __name__ == "__main__":
    asyncio.run(run_browser_tasks())