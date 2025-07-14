from src.browser import get_browser_page
from src.consts import input_eval_js
from src.oxylabs.proxy import get_proxy_given_country
import asyncio
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlencode, urlparse
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
            # await self.page.goto('https://api.ipify.org?format=json')
            # content = await self.page.content()
            # startIndex = content.find('{')
            # endIndex = content.rfind('}')
            # content = content[startIndex:endIndex + 1]
            # data = json.loads(content)
            # publicIP = data['ip']
            # print(f"Public IP: {publicIP}")
            # print(f"Navigating to {url}")
            # await self.page.goto(f'https://ip-api.com/line/{publicIP}')
            # content = await self.page.content()
            # print(content)
            print(f"Navigating to {url}")
            await self.page.goto(url, {"waitUntil": "networkidle2", "timeout": 60000})
            print(f"Navigated to {url}")
            html = await self.page.content()
            print(f"HTML fetched for {url}")
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

            def remove_trailing_slash(url: str):
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
                        search_url = f"{remove_trailing_slash(url)}{get_action_path(form['action'])}?{input['name']}=iphone"
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
            await page.screenshot({'path': 'screenshot.png'})
        except Exception as e:
            pass
        print(e)
        return None
    finally:
        if browser:
            await browser.close()



async def run_browser_tasks():
    task_browser = BrowserTask("in")
    
    websites = ['https://www.tatacliq.com', 'https://www.jiomart.com', 'https://www.boat-lifestyle.com', 'https://www.moglix.com', 'https://www.reliancedigital.in', 'https://play.google.com', 'https://www.smartprix.com', 'https://www.swiggy.com', 'https://www.flipkart.com', 'https://blinkit.com', 'https://www.bigbasket.com', 'https://www.91mobiles.com', 'https://www.poorvika.com', 'https://www.zeptonow.com', 'https://dir.indiamart.com', 'https://www.ajio.com', 'https://www.myntra.com', 'https://www.vijaysales.com', 'https://m.snapdeal.com', 'https://www.croma.com', 'https://www.nykaafashion.com']
    
    # Sequential execution
    for url in websites:
        await task_browser.get_html(url)
    
    await task_browser.cleanup()

if __name__ == "__main__":
    asyncio.run(run_browser_tasks())