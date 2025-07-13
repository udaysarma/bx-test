from oxylabs.locations import locations
import os
from dotenv import load_dotenv

load_dotenv()

OX_USERNAME=os.getenv("OX_USERNAME")
OX_PASSWORD=os.getenv("OX_PASSWORD")

def get_proxy_given_country(country_code: str, authenticated: bool = False) -> str:
    for location in locations:
        if location['domain'].split('-')[0].strip().lower() == country_code.lower():
            if authenticated:
                return f"https://{OX_USERNAME}:{OX_PASSWORD}@{location['proxy']}"
            else:
                return f"https://{location['proxy']}"
    raise Exception('location not found')
