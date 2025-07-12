import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, urljoin

# Check if the text looks like a price
# This function uses regex to find common price formats like ₹, $, €, £ followed by numbers, add more currencies as needed
def looks_like_price(text):
    return bool(re.search(r'₹[\d,]+|[$€£¥₹₩₽₺R$₱₪₫₭₦₲฿₡₵₮ƒ]\s?[\d,]+', text))


# Extract products from the HTML content
# This function looks for common product containers and extracts title, price, link, and image
def extract_products(html):
    soup = BeautifulSoup(html, 'html.parser')
    candidates = soup.find_all(['div', 'li', 'section', 'article'])

    products = []

    for tag in candidates:
        text = tag.get_text(separator=' ', strip=True)
        price_match = looks_like_price(text)
        a_tag = tag.find('a', href=True)
        img_tag = tag.find('img')
        title = None

        if a_tag:
            title = a_tag.get_text(strip=True, separator=' ') or tag.get('alt', '').strip()

        if price_match and a_tag and title:
            products.append({
                'title': title,
                'price': re.search(r'₹[\d,]+|[$€£]\s?[\d,]+', text).group(),
                'link': a_tag['href'],
                'image': img_tag['src'] if img_tag and img_tag.has_attr('src') else None
            })

    return products


# Extract pagination links from the HTML content
# Collect all links that *look like* pagination
def get_pagination_links(url, content):
    soup = BeautifulSoup(content, 'html.parser')

    pagination_links = set()
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True).lower()
        if text.isdigit() or any(word in text for word in ['next', 'prev', 'previous', 'last', 'first']):
            full_url = urljoin(url, a['href'])
            pagination_links.add(full_url)

    return sorted(pagination_links)


# Get the query parameter match and update it with the new query
# This function updates the query parameter in the URL with the new query
def get_qp_match(query_params, query, text='iphone') -> list:
    for i, (key, value) in enumerate(query_params):
        if value == text:
            query_params[i] = (key, query)  # Update the value with the new query
            return query_params

    for i, (key, value) in enumerate(query_params):
        if value == '' or value is None:
            query_params[i] = (key, query)
    return query_params

def reencode_url_with_new_query(url: str, new_query: str) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qsl(parsed_url.query, keep_blank_values=True)
    matches = get_qp_match(query_params, new_query)
    new_query_string = urlencode(matches, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query_string))
    
    return new_url
