from pyppeteer import launch
import asyncio

async def fetch_html(url: str) -> str:
    print(f"Fetching HTML for URL: {url}")
    browser = await launch(executablePath="/usr/bin/chromium-browser", headless=True, args=["--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-infobars",
        "--window-size=1920,1080"])
    print("Browser launched")
    page = await browser.newPage()
    print("New page created")
    await page.goto(url, {"waitUntil": "networkidle2"})
    print(f"Page loaded: {url}")
    content = await page.content()
    print("Content fetched")
    await browser.close()
    print("Browser closed")
    print("Returning content")
    return content

def test_fetch_html():
    url = "http://google.com"
    loop = asyncio.get_event_loop()
    html_content = loop.run_until_complete(fetch_html(url))
    print("HTML content fetched successfully")
    print(html_content[:1000])  # Print first 1000 characters for brevity
    assert "<title>Example Domain</title>" in html_content, "HTML content does not contain expected title"
    print("Test passed: HTML content contains expected title")

if __name__ == "__main__":
    test_fetch_html()
    print("Test completed successfully")