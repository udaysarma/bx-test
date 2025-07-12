from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import redis
from src.browser_actions import get_navigation_url, search_query, fetch_html
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
        html = await fetch_html(url, country)
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
        navigation_url = await get_navigation_url(url, country)
        return JSONResponse(status_code=200, content={"navigation_url": navigation_url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


class SearchRequest(BaseModel):
    url: str
    css_path: str
    q: str

@app.post("/api/search", response_class=HTMLResponse)
async def search(request: SearchRequest):
    url = request.url
    try:
        print(f"Received URL for search: {url}")
        if not url.startswith("http://") and not url.startswith("https://"):
            return JSONResponse(status_code=400, content={"error": "Invalid URL format. URL must start with http:// or https://"})
        content = await search_query(url, request.css_path, request.q)
        return HTMLResponse(content=content, status_code=200)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/search", response_class=JSONResponse)
async def read_root(q: str = None, searchId: str = None, country: str = None):
    # type of websites -- ecommerce, brand websites.
    # create new uuid
    search_manager = SearchManager(r)
    # if searchId == "":
    #     print(f"Received searchId: {searchId}")
    #     results = await search_manager.get_search_results("c9766c17-4c0f-40b0-b2b5-ffc9774343d3")
    #     return JSONResponse(status_code=200, content={
    #         "products": results.get("results", []),
    #         "total": len(results.get("results", [])),
    #         "searchId": searchId
    #     })
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
    
