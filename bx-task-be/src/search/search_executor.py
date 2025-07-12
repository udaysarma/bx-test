import asyncio
import redis
from multiprocessing import Process
import psutil
from typing import Optional, Union

from src.search.search_db import SearchManager
from src.browser_actions import BrowserTask
from src.process_data import extract_products, reencode_url_with_new_query

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Limit concurrent tasks to prevent overwhelming the system
semaphore = asyncio.Semaphore(30)

async def limited_task(coro):
    async with semaphore:
        return await coro

def run_search_process(search_id: str, query: str, country: str):
    """Run the search process in a separate process."""
    asyncio.run(execute_new_search(search_id, query, country))

def kill_process_and_children(pid: int):
    """Kill a process and all its child processes."""
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

def start_or_restart_search(search_id: str, query: str, country: str):
    """Start a new search process or restart an existing one."""
    redis_key = "search_process"

    # Kill old process if it exists
    old_pid: Optional[Union[bytes, str]] = redis_client.get(redis_key)
    print(f"Old process ID: {old_pid}")
    if old_pid is not None:
        try:
            if isinstance(old_pid, bytes):
                kill_process_and_children(int(old_pid.decode('utf-8')))
            else:
                kill_process_and_children(int(old_pid))
        except (ValueError, AttributeError):
            print("Failed to decode old process ID")

    # Start new process
    process = Process(target=run_search_process, args=(search_id, query, country))
    process.start()

    # Save new PID
    redis_client.set(redis_key, str(process.pid))
    print(f"Started new process {process.pid} for search {search_id}")


async def execute_new_search(search_id: str, query: str, country: str):
    """Execute a new search across multiple websites."""
    search_manager = SearchManager(redis_client)
    browser_task = BrowserTask(country)
    while True:
        try:
            new_website_to_scrape = await search_manager.get_new_website_for_scraping(search_id)
            if not new_website_to_scrape:
                print("No more websites to scrape.")
                break

            print(f"Scraping {new_website_to_scrape} for {query}")
            # if 'amazon' in new_website_to_scrape:
            #     continue
            url = await asyncio.wait_for(browser_task.get_navigation_url(new_website_to_scrape, country), timeout=60)
            if not url:
                print(f"Failed to get navigation URL for {new_website_to_scrape}. Skipping.")
                continue
                
            search_url = reencode_url_with_new_query(url, query)
            html_content = await asyncio.wait_for(browser_task.get_html(search_url), timeout=60)
            if html_content is None:
                print(f"Failed to get HTML content for {new_website_to_scrape}. Skipping.")
                continue
                
            products = extract_products(html_content)
            print(f"Extracted {len(products)} products from {search_url}")

            tasks = [
                limited_task(search_manager.check_if_result_is_valid_and_save(
                    search_id, query, product, new_website_to_scrape
                )) for product in products
            ]
            results = await asyncio.gather(*tasks)
        
        except Exception as e:
            print(f"An error occurred: {e}")
    await browser_task.cleanup()

def get_existing_search(query: str, country: str) -> Optional[str]:
    """Retrieve the existing search ID from Redis."""
    search_id: Optional[Union[bytes, str]] = redis_client.get(f"search:{query}:{country}")
    if search_id is None:
        return None
    try:
        if isinstance(search_id, bytes):
            return search_id.decode('utf-8')
        return str(search_id)
    except (ValueError, AttributeError):
        return None

if __name__ == "__main__":
    # Example usage for testing
    asyncio.run(execute_new_search("test_search_id", "iphone 16 pro max", "US"))
