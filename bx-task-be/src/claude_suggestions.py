import asyncio
from playwright.async_api import async_playwright
import time
import random
from urllib.parse import urljoin, urlparse
import re

async def use_site_search_playwright(domain, query, options=None):
    """
    Search a site using Playwright for dynamic content
    """
    if options is None:
        options = {}
    
    headless = options.get('headless', True)
    timeout = options.get('timeout', 30000)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--disable-gpu'
            ]
        )
        
        page = await browser.new_page()
        
        try:
            # Set user agent and viewport
            await page.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            await page.set_viewport_size({"width": 1366, "height": 768})
            
            # Block unnecessary resources
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", lambda route: route.abort())
            
            # Navigate to the domain
            await page.goto(domain, wait_until='domcontentloaded', timeout=timeout)
            
            # Handle popups/cookie banners
            await handle_popups(page)
            
            # Find search input
            search_input = await find_search_input(page)
            if not search_input:
                print(f"No search input found on {domain}")
                return []
            
            # Perform search
            await perform_search(page, search_input, query)
            
            # Wait for results
            await wait_for_search_results(page)
            
            # Extract product links
            product_links = await extract_product_links(page, domain)
            
            return product_links
            
        except Exception as e:
            print(f"Error searching {domain}: {str(e)}")
            return []
        finally:
            await browser.close()

async def handle_popups(page):
    """Handle cookie banners and popups"""
    popup_selectors = [
        '.cookie-banner button',
        '.cookie-notice button',
        '.modal-close',
        '.popup-close',
        '[aria-label="Close"]',
        '.close-button',
        '#cookie-accept',
        '.accept-cookies'
    ]
    
    for selector in popup_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                await element.click()
                await page.wait_for_timeout(500)
        except:
            continue

async def find_search_input(page):
    """Find search input using multiple selectors"""
    search_selectors = [
        'input[type="search"]',
        'input[name*="search" i]',
        'input[name*="query" i]',
        'input[name="q"]',
        'input[placeholder*="Search" i]',
        'input[placeholder*="search" i]',
        '#search-input',
        '#search',
        '.search-input',
        '.search-field',
        '[data-testid*="search"]',
        '[aria-label*="Search" i]'
    ]
    
    for selector in search_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                # Check if element is visible
                is_visible = await element.is_visible()
                if is_visible:
                    print(f"Found search input with selector: {selector}")
                    return element
        except:
            continue
    
    return None

async def perform_search(page, search_input, query):
    """Perform the search operation"""
    try:
        # Click and clear the input
        await search_input.click()
        await search_input.fill('')  # Clear existing value
        
        # Type the query with human-like delay
        await search_input.type(query, delay=100)
        
        # Try multiple ways to submit the search
        try:
            # Method 1: Press Enter
            await search_input.press('Enter')
        except:
            # Method 2: Find and click search button
            search_buttons = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.search-button',
                '#search-button',
                'button:has-text("Search")',
                'button:has-text("search")'
            ]
            
            for button_selector in search_buttons:
                try:
                    button = await page.query_selector(button_selector)
                    if button:
                        await button.click()
                        break
                except:
                    continue
    
    except Exception as e:
        print(f"Error performing search: {str(e)}")
        # Try pressing Enter one more time
        await search_input.press('Enter')

async def wait_for_search_results(page):
    """Wait for search results to load"""
    result_selectors = [
        '.search-results',
        '.products',
        '.product-list',
        '.results',
        '[data-testid*="search-results"]',
        '.product-grid',
        '.search-result'
    ]
    
    # Wait for any of these selectors or timeout
    try:
        await page.wait_for_selector(','.join(result_selectors), timeout=5000)
    except:
        # If no specific results container found, wait a bit anyway
        await page.wait_for_timeout(3000)

async def extract_product_links(page, base_domain):
    """Extract product links from search results"""
    product_selectors = [
        'a[href*="product"]',
        'a[href*="item"]',
        'a[href*="/p/"]',
        'a[href*="/dp/"]',      # Amazon
        'a[href*="/itm/"]',     # eBay
        'a[href*="/products/"]',
        '.product-item a',
        '.product-link',
        '.product-title a',
        '.product-name a',
        '[data-testid*="product"] a',
        '.product-card a'
    ]
    
    links = []
    
    for selector in product_selectors:
        try:
            elements = await page.query_selector_all(selector)
            
            for element in elements:
                href = await element.get_attribute('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_domain, href)
                    links.append(full_url)
            
            if links:
                break  # If we found links with this selector, use them
                
        except Exception as e:
            continue
    
    # Remove duplicates and filter valid URLs
    unique_links = list(set(links))
    base_hostname = urlparse(base_domain).hostname
    
    # Filter to only include links from the same domain
    filtered_links = [
        link for link in unique_links 
        if base_hostname in link or link.startswith(base_domain)
    ]
    
    return filtered_links

# Enhanced version with retries and better error handling
async def use_site_search_playwright_advanced(domain, query, options=None):
    """
    Advanced version with retry logic and better error handling
    """
    if options is None:
        options = {}
    
    max_retries = options.get('max_retries', 3)
    delay = options.get('delay', 1000)
    
    for attempt in range(1, max_retries + 1):
        try:
            result = await use_site_search_playwright(domain, query, options)
            if result:  # If we got results, return them
                return result
        except Exception as e:
            print(f"Attempt {attempt} failed for {domain}: {str(e)}")
            
            if attempt < max_retries:
                # Wait before retrying
                await asyncio.sleep(delay * attempt / 1000)
            else:
                print(f"Failed to search {domain} after {max_retries} attempts")
                return []
    
    return []

# Site-specific search patterns
def get_site_specific_search_url(domain, query):
    """Get search URL for known platforms"""
    from urllib.parse import quote
    
    domain_lower = domain.lower()
    encoded_query = quote(query)
    
    if 'amazon' in domain_lower:
        return f"{domain}/s?k={encoded_query}"
    elif 'ebay' in domain_lower:
        return f"{domain}/sch/i.html?_nkw={encoded_query}"
    elif 'shopify' in domain_lower:
        return f"{domain}/search?q={encoded_query}"
    elif 'etsy' in domain_lower:
        return f"{domain}/search?q={encoded_query}"
    elif 'walmart' in domain_lower:
        return f"{domain}/search?q={encoded_query}"
    else:
        return None

# Hybrid approach combining direct URL access and dynamic search
async def hybrid_site_search(domain, query, options=None):
    """
    Try direct search URL first, then fall back to dynamic search
    """
    if options is None:
        options = {}
    
    # Try direct search URL first
    direct_url = get_site_specific_search_url(domain, query)
    if direct_url:
        try:
            # Use requests or httpx for simple HTTP request
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(direct_url, timeout=10)
                if response.status_code == 200:
                    # Parse with BeautifulSoup
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = extract_product_links_from_html(soup, domain)
                    if links:
                        return links
        except:
            pass
    
    # Fall back to dynamic search
    return await use_site_search_playwright_advanced(domain, query, options)

def extract_product_links_from_html(soup, base_domain):
    """Extract product links from HTML using BeautifulSoup"""
    product_selectors = [
        'a[href*="product"]',
        'a[href*="item"]',
        'a[href*="/p/"]',
        'a[href*="/dp/"]',
        'a[href*="/products/"]'
    ]
    
    links = []
    for selector in product_selectors:
        elements = soup.select(selector)
        for element in elements:
            href = element.get('href')
            if href:
                full_url = urljoin(base_domain, href)
                links.append(full_url)
    
    return list(set(links))

# Batch processing function
async def search_multiple_sites(domains, query, options=None):
    """
    Search multiple sites concurrently
    """
    if options is None:
        options = {}
    
    max_concurrent = options.get('max_concurrent', 3)
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def search_single_site(domain):
        async with semaphore:
            print(f"Searching {domain} for '{query}'...")
            
            # Add random delay to avoid being detected
            await asyncio.sleep(random.uniform(1, 3))
            
            product_links = await hybrid_site_search(domain, query, options)
            
            result = {
                'domain': domain,
                'query': query,
                'product_links': product_links,
                'count': len(product_links)
            }
            
            print(f"Found {len(product_links)} products on {domain}")
            return result
    
    # Create tasks for all domains
    tasks = [search_single_site(domain) for domain in domains]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and return valid results
    valid_results = [r for r in results if not isinstance(r, Exception)]
    return valid_results

# Usage example
async def main():
    domains = [
        'https://www.amazon.in',
        'https://www.flipkart.com',
        'https://www.tataclip.com'
    ]
    
    query = 'wireless headphones'
    
    options = {
        'headless': True,
        'timeout': 30000,
        'max_retries': 2,
        'max_concurrent': 3
    }
    
    results = await search_multiple_sites(domains, query, options)
    
    # Process results
    for result in results:
        print(f"\n{result['domain']}:")
        print(f"Found {result['count']} products")
        
        # Print first 5 links
        for link in result['product_links'][:5]:
            print(f"- {link}")

if __name__ == "__main__":
    # Install required packages first:
    # pip install playwright beautifulsoup4 httpx
    # playwright install chromium
    
    asyncio.run(main())