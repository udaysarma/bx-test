import asyncio
from urllib.parse import urlparse
from src.search.search_db import SearchManager
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def get_domain_from_url(url):
    return urlparse(url).scheme + '://' + urlparse(url).netloc

async def add_baidu_search_to_db(query, search, country, search_id):
    print(f"Adding baidu search to db for query: {query}, country: {country}, search_id: {search_id}")
    organic_results = search['organic_results']
    valid_results = []
    search_manager = SearchManager(r)
    for result in organic_results:
        title = result['title']
        link = result.get('link', None)
        snippet = result.get('snippet', None)
        valid_results.append({
            'title': title,
            'link': link,
            'snippet': snippet
        })
    tasks = [search_manager._save_result(search_id, p, p, get_domain_from_url(p['link'])) for p in valid_results]
    return None

async def add_google_search_to_db(query, search, country, search_id):
    print(f"Adding google search to db for query: {query}, country: {country}, search_id: {search_id}")
    organic_results = search['organic_results']
    valid_results = []
    for result in organic_results:
        title = result['title']
        link = result['link']
        print(result.keys(), result['link'])
        currency = result.get('rich_snippet', {}).get('bottom', {}).get('detected_extensions', {}).get('currency', None)
        price = result.get('rich_snippet', {}).get('bottom', {}).get('detected_extensions', {}).get('price', None)
        price_from = result.get('rich_snippet', {}).get('bottom', {}).get('detected_extensions', {}).get('price_from', None)
        price_to = result.get('rich_snippet', {}).get('bottom', {}).get('detected_extensions', {}).get('price_to', None)
        if not currency:
            continue
        if price:
            valid_results.append({
                'title': title,
                'link': link,
                'image': result.get('favicon', None),
                'currency': currency,
                'price': currency+str(price)
            })
        elif price_from and price_to:
            valid_results.append({
                'title': title,
                'link': link,
                'image': result.get('favicon', None),
                'price_from': currency+str(price_from),
                'price_to': currency+str(price_to)
            })

    search_manager = SearchManager(r)
    tasks = [search_manager.check_if_result_is_valid_and_save(search_id, query, p, get_domain_from_url(p['link'])) for p in valid_results]
    results = await asyncio.gather(*tasks)
