from src.browser import get_browser_page
from src.consts import input_eval_js
from src.oxylabs.proxy import get_proxy_given_country
import asyncio
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlencode, urlparse
from typing import List, Dict, Any, Optional
import redis

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


async def get_navigation_url_with_form(url: str, country: str):
    html = get_proxied_html(url, country)
    if not html:
        return None, None
    soup = BeautifulSoup(html, 'html.parser')
    form = soup.find('form')
    if not form:
        return None, None
    return form.get('action'), form.get('method')

async def get_navigation_url(url: str, country: str):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    search_url = redis_client.get(f"{domain}:{country}:search_url")
    if search_url:
        return search_url.decode('utf-8')

    proxy = get_proxy_given_country(country)
    print(f"found proxy {proxy}")
    try:
        browser, page = await get_browser_page(proxy)

        print("abcd")

        await page.goto(url, {"waitUntil": "networkidle2"})
        # print(len(form_handle), "forms found")

        # forms_text = await page.evaluate('''() => {
        #     const forms = Array.from(document.querySelectorAll('form'));
        #     return forms.map(form => form.innerText.trim());
        # }''')

        # # Print each form's text
        # for i, text in enumerate(forms_text):
        #     print(f"Form {i + 1} text:\n{text}\n{'-'*40}")

        # Find the input inside the form
        input_selector = 'input[type="text"], input[type="search"], textarea'  # Adjust this selector
        # input_handle = await form_handle.querySelector(input_selector)
        # first_text_input = await page.querySelector(input_selector)

        html = await page.content()
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
                if input['type'] == 'text' or input['type'] == 'search':
                    if 'search' in json.dumps(input).lower():
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
            await page.screenshot({'path': 'screenshot.png'})
        except Exception as e:
            pass
        print(e)
        return None
    finally:
        if browser:
            await browser.close()

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


async def fetch_html(url: str, country: str) -> str:
    print(f"Fetching HTML for URL: {url}")
    proxy = get_proxy_given_country(country)
    try: 
        browser, page = await get_browser_page(proxy)
        print("New page created")
        await page.goto(url, {"waitUntil": "networkidle2"})
        print(f"Page loaded: {url}")
        content = await page.content()
        await browser.close()

        print("Browser closed")
        print("Returning content")
        return content
    except Exception as e:
        print(e)
        return ""


if __name__ == "__main__":
    for i in [
    "https://www.boostmobile.com",
    "https://www.metrobyt-mobile.com",
    "https://www.youtube.com",
    "https://www.reddit.com",
    "https://www.xfinity.com",
    "https://www.bestbuy.com",
    "https://discussions.apple.com",
    "https://www.dpreview.com",
    "https://forums.appleinsider.com",
    "https://www.cspire.com",
    "https://forums.macrumors.com",
    "https://www.forbes.com",
    "https://www.att.com",
    "https://www.spectrum.com",
    "https://www.apple.com",
    "https://www.walmart.com",
    "https://www.macofalltrades.com",
    "https://community.verizon.com",
    "https://www.amazon.com",
    "https://buy.gazelle.com",
    "https://www.puretalk.com",
    "https://applemania.quora.com",
    "https://forums.guru3d.com",
    "https://www.zdnet.com",
    "https://www.t-mobile.com",
    "https://www.pcmag.com",
    "https://www.visible.com"
    ]:
        asyncio.run(get_navigation_url(i, "us"))
