from src.browser import get_browser_page
from src.consts import input_eval_js
from src.oxylabs.proxy import get_proxy_given_country
import asyncio

async def get_navigation_url(url: str, country: str):
    proxy = get_proxy_given_country(country)
    print(f"found proxy {proxy}")
    try:
        browser, page = await get_browser_page(proxy)

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

        # if input_handle:
        #     await input_handle.type('iphone')
        #     await asyncio.gather(
        #         page.evaluate('''() => {
        #             document.querySelector('form').submit();
        #         }'''),
        #         page.waitForNavigation(timeout=10000)
        #     )
        #     print("Typed into input field inside the form.")
        # elif first_text_input:
        #     await first_text_input.type('iphone')
        #     await asyncio.gather(
        #         page.keyboard.press('Enter'),
        #         page.waitForNavigation(timeout=10000)
        #     )
        #     print("Input field not found inside the form.")
        # else:
        #     return None

        # Define coroutines to get the handles
        async def get_input_handle():
            await page.waitForSelector('form')
            print("Form found, typing into the input field...")
            form_handle = await page.querySelector('form')

            handle = await form_handle.querySelector(input_selector)
            return 'form', handle if handle else None

        async def get_first_text_input():
            await page.waitForSelector(input_selector)
            handle = await page.querySelector(input_selector)
            return 'non_form', handle if handle else None

        async def get_first_text_area():
            await page.waitForSelector('textarea')
            handle = await page.querySelector('textarea')
            return 'textarea', handle if handle else None

        # Run both and wait for the first one that returns a non-None handle
        tasks = [
            asyncio.create_task(get_input_handle()),
            asyncio.create_task(get_first_text_input()),
            # asyncio.create_task(get_first_text_area())
        ]

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        result_type, handle = None, None
        for task in done:
            result_type, handle = await task
            if handle:
                break

        # Cancel any remaining tasks
        for task in pending:
            task.cancel()

        print('k')
        print(result_type, handle)

        # Proceed based on which input was found
        if handle:
            await handle.type('iphone', delay=10)  # Type the query with a slight delay for realism

            if result_type == 'form':
                await asyncio.gather(
                    page.evaluate('''() => {
                        document.querySelector('form').submit();
                    }'''),
                    page.waitForNavigation()
                )
                print("Typed into input field inside the form.")
            else:
                await asyncio.gather(
                    page.keyboard.press('Enter'),
                    page.waitForNavigation()
                )
                print("Input field not inside the form.")
        else:
            print("No input field found.")
            return None

        # Submit the form via JavaScript
        # await asyncio.gather(
        #     page.evaluate('''() => {
        #         document.querySelector('form').submit();
        #     }'''),
        #     page.waitForNavigation(timeout=10000)
        # )
        print(page.url)
        return page.url
    except Exception as e:
        await page.screenshot({'path': 'screenshot.png'})
        print(e)
        return None
    finally:
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
        return ""


if __name__ == "__main__":
    asyncio.run(get_navigation_url("https://www.bestbuy.com", "us"))
