from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import redis
from src.browser_actions import BrowserTask
from src.search.search_db import SearchManager
from src.search.search_executor import start_or_restart_search, get_existing_search
from src.serp.serp import get_all_domains
from src.search.helper import add_google_search_to_db, add_baidu_search_to_db

r = redis.Redis(host='localhost', port=6379, db=0)
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str
    country: str

@app.post("/api/scrape", response_class=JSONResponse)
async def scrape(request: ScrapeRequest):
    url = request.url
    country = request.country
    try:
        print(f"Received URL: {url}")
        if not url.startswith("http://") and not url.startswith("https://"):
            return JSONResponse(status_code=400, content={"error": "Invalid URL format. URL must start with http:// or https://"})
        browser_task = BrowserTask(country)
        html = await browser_task.get_html(url)
        await browser_task.cleanup()
        return html
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


class NavigationUrlRequest(BaseModel):
    url: str
    country: str

@app.post("/api/navigate", response_class=JSONResponse)
async def navigate(request: NavigationUrlRequest):
    url = request.url
    country = request.country
    print(f"Received URL for navigation: {url}")
    try:
        print(f"Received URL for navigation: {url}")
        if not url.startswith("http://") and not url.startswith("https://"):
            return JSONResponse(status_code=400, content={"error": "Invalid URL format. URL must start with http:// or https://"})
        browser_task = BrowserTask(country)
        navigation_url = await browser_task.get_navigation_url(url, country)
        await browser_task.cleanup()
        return JSONResponse(status_code=200, content={"navigation_url": navigation_url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



@app.get("/api/search", response_class=JSONResponse)
async def read_root(q: str = None, searchId: str = None, country: str = None):
    search_manager = SearchManager(r)
    if not q or not country:
        return JSONResponse(status_code=400, content={"error": "Query parameter 'q' is required"})
    print(f"Received query: {q}")
    search_id = get_existing_search(q, country)
    if search_id:
        print(f"Found existing search ID: {search_id} for query: {q}")
        results = await search_manager.get_search_results(search_id)
        return JSONResponse(status_code=200, content={
            "products": results.get("results", []),
            "total": len(results.get("results", [])),
            "searchId": search_id
        })
    else:
        print(f"No existing search ID found for query: {q}, starting a new search")
        search, websites = get_all_domains(q, country)
        print(f"Starting a new search for query: {q}, country: {country}, websites: {websites}")
        search_id = await search_manager.start_a_search(q, country, websites)
        if country.lower() == "cn":
            asyncio.create_task(add_baidu_search_to_db(q, search, country, search_id))
        else:
            asyncio.create_task(add_google_search_to_db(q, search, country, search_id))
        r.set(f"search:{q}:{country}", search_id)
        start_or_restart_search(search_id, q, country)
    return JSONResponse(status_code=200, content={
        "products": [],
        "total": 0,
        "searchId": searchId
    })
    
