from src.oxylabs.locations import locations
import os
from dotenv import load_dotenv

load_dotenv()

OX_USERNAME=os.getenv("OX_USERNAME")
OX_PASSWORD=os.getenv("OX_PASSWORD")

def get_proxy_given_country(country_code: str, authenticated: bool = False) -> str:
    for location in locations:
        if location['proxy'].split('-')[0].strip() == country_code:
            if authenticated:
                return f"https://{OX_USERNAME}:{OX_PASSWORD}@{location['proxy']}"
            else:
                return f"https://{location['proxy']}"
    raise Exception('location not found')
