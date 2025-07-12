import requests
from src.serp.locations import locations
from src.oxylabs.proxy import get_proxy_given_country
from urllib.parse import urlencode, urlparse
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")

class Serp:
    def __init__(self):
        self.serp_api_key = SERP_API_KEY
        self.serp_api_url = "https://serpapi.com/search"

    def serp_results_search(self, query, country_code="IN"):
        params = self._get_search_query_params(query, country_code, "google")
        return self._get_serp_results(params)


    def serp_shopping_search(self, query, country_code="IN"):
        params = self._get_search_query_params(query, country_code, "google_shopping")
        return self._get_serp_results(params)


    def _get_country_code_from_name(self, name):
        for location in locations:
            if location["country_code"].lower() == name.lower():
                return location
        return locations[30]

    def _get_search_query_params(self, query, country_code="IN", search_type="google"):
        location = self._get_country_code_from_name(country_code)
        return {
            "q": "buy " + query,
            "location": location["country_name"],
            "engine": search_type,
            "hl": location["language_code"],
            "gl": location["country_code"],
            "google_domain": location["domain"],
            "api_key": SERP_API_KEY,
            "num": 30
        }

    def _get_serp_results(self, params):
        response = requests.get(f"{self.serp_api_url}?{urlencode(params)}")
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return {}
        return response.json()


serp_api = Serp()

def get_proxied_html(url, country_code="IN"):
    proxy = get_proxy_given_country(country_code, authenticated=True)

    response = requests.get(url, proxies={
        "http": proxy,
        "https": proxy
    })
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return {}
    return response.text


def get_all_domains(query, country_code="IN"):
    search = serp_api.serp_results_search(query, country_code)
    return search, list(set([urlparse(result["link"]).scheme + "://" + urlparse(result["link"]).netloc for result in search["organic_results"]]))


def get_all_shopping_domains(query, country_code="IN"):
    def domain_from_url(link):
        parsed = urlparse(link)
        return parsed.scheme + "://" + parsed.netloc

    shopping = serp_api.serp_shopping_search(query, country_code)
    if "shopping_results" not in shopping:
        return []

    shopping_results = shopping["shopping_results"]
    all_domains = set()
    for shopping_result in shopping_results:
        html = get_proxied_html(shopping_result["product_link"], country_code)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        links = [a["href"] for a in soup.find_all('a', href=True)]
        all_domains.update([domain_from_url(link[7:]) for link in links if link.startswith('/url?q=')])
        print(len(all_domains))
        return shopping, [link[7:] for link in links if link.startswith('/url?q=')]
    return shopping, list(all_domains)


if __name__=="__main__":
    shopping, websites = get_all_domains("iphone 16 pro max", 'us')
    print(shopping)
    print(websites)

