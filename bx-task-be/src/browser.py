from pyppeteer import launch
from pyppeteer_stealth import stealth

import os

OX_USERNAME=os.getenv("OX_USERNAME")
OX_PASSWORD=os.getenv("OX_PASSWORD")

async def get_browser_page(proxy: str):
    browser = await launch({
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
                '--proxy-server=' + proxy
            ],
            'ignoreHTTPSErrors': True,
        })

    print(f"Using proxy {proxy}", '--proxy-server=' + proxy)

    page = await browser.newPage()

    await page.authenticate({
        'username': OX_USERNAME,
        'password': OX_PASSWORD'
    })

    await stealth(page)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    await page.setUserAgent(user_agent)
    await page.setViewport({'width': 1280, 'height': 800})

    print("New page created")
    return browser, page
