from pyppeteer import launch
from pyppeteer_stealth import stealth
from dotenv import load_dotenv
import asyncio

load_dotenv()

import os

OX_USERNAME=os.getenv("OX_USERNAME", "")
OX_PASSWORD=os.getenv("OX_PASSWORD", "")

async def get_browser_page(proxy: str):
    print("Launching browser", proxy)
    browser = await launch({
            # 'executablePath': '/usr/bin/chromium-browser',
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-sync',
                '--disable-translate',
                '--hide-scrollbars',
                '--mute-audio',
                '--disable-background-networking',
                '--disable-default-apps',
                '--no-default-browser-check',
                '--no-pings',
                '--single-process',
                '--disable-ipc-flooding-protection',
                '--memory-pressure-off',
                '--proxy-server=' + proxy,
                # '--proxy-auth=' + OX_USERNAME + ':' + OX_PASSWORD
            ],
            'ignoreHTTPSErrors': True,
        })

    print(f"Using proxy {proxy}", '--proxy-server=' + proxy)

    page = await browser.newPage()

    # await page.setRequestInterception(True)
    
    # # Define request handler using page.on with proper async handling
    # async def handle_request(request):
    #     try:
    #         url = request.url.lower()
            
    #         # Block by resource type (most reliable method)
    #         if request.resourceType == 'image':
    #             await request.abort()
    #             print(f"Blocked image: {request.url}")
    #         # Also block by file extension as backup
    #         elif any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']):
    #             await request.abort()
    #             print(f"Blocked image by extension: {request.url}")
    #         else:
    #             await request.continue_()
    #     except Exception as e:
    #         print(f"Error handling request {request.url}: {e}")
    #         # Try to continue the request if abort/continue failed
    #         try:
    #             await request.continue_()
    #         except:
    #             pass
    
    # # Set up the request interception using addListener for proper async handling
    # page.on('request', lambda req: asyncio.create_task(handle_request(req)))

    # intercept images and stop them from loading
    # await page.setRequestInterception(True)
    # def intercept_images(request):
    #     if request.resourceType == 'image':
    #         request.abort()

    # page.on('request', intercept_images)

    await stealth(page)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    await page.setUserAgent(user_agent)
    await page.setViewport({'width': 1280, 'height': 800})

    await page.setExtraHTTPHeaders({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

    await page.authenticate({
        'username': OX_USERNAME,
        'password': OX_PASSWORD
    })

    print("New page created")

    return browser, page
