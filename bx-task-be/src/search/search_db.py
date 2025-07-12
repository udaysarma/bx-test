import uuid
import json
from typing import Optional, Dict, List, Any, Union
from src.consts import websites_to_search
from src.llm_helper import check_if_valid_search_result
from urllib.parse import urlparse

class SearchManager:
    """Manages search operations and results storage in Redis."""
    
    def __init__(self, redis_client):
        """Initialize SearchManager with a Redis client.
        
        Args:
            redis_client: Redis client instance for data storage
        """
        self.redis_client = redis_client

    async def start_a_search(self, query: str, country: str, websites: List[str]) -> str:
        """Start a new search and initialize storage.
        
        Args:
            query: Search query string
            country: Country code for the search
            websites: List of websites to search
            
        Returns:
            str: Generated search ID
        """
        search_id = str(uuid.uuid4())
        print(f"Starting a new search with ID: {search_id}")
        self.redis_client.set(f"{search_id}:websites", json.dumps(websites))
        self.redis_client.set(f"{search_id}:results", "[]")
        return search_id

    async def get_search_results(self, search_id: str) -> Dict[str, Any]:
        """Retrieve search results from Redis.
        
        Args:
            search_id: Search identifier
            
        Returns:
            Dict containing search results or error message
        """
        print(f"Fetching results for search ID: {search_id}")
        results_data = self.redis_client.get(f"{search_id}:results")
        if results_data is None:
            return {"error": "No results found for this search ID."}
        
        try:
            results = json.loads(results_data.decode('utf-8'))
            return {
                "search_id": search_id,
                "results": results
            }
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error decoding results: {e}")
            return {"error": "Failed to decode search results."}

    async def get_new_website_for_scraping(self, search_id: str) -> Optional[str]:
        """Get the next website to scrape from the queue.
        
        Args:
            search_id: Search identifier
            
        Returns:
            str: Next website URL or None if no websites remain
        """
        print(f"Fetching new website for scraping for search ID: {search_id}")
        websites_data = self.redis_client.get(f"{search_id}:websites")
        if websites_data is None:
            return None
        
        try:
            websites_list = json.loads(websites_data.decode('utf-8'))
            if not websites_list:
                return None
            
            next_website = websites_list.pop(0)
            self.redis_client.set(f"{search_id}:websites", json.dumps(websites_list))
            return next_website
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error decoding websites list: {e}")
            return None

    async def check_if_result_is_valid_and_save(
        self, 
        search_id: str, 
        query: str, 
        result: Dict[str, Any], 
        url: str
    ) -> Optional[Dict[str, str]]:
        """Validate and save a search result.
        
        Args:
            search_id: Search identifier
            query: Original search query
            result: Product result data
            url: Source website URL
            
        Returns:
            Dict with success/error message or None if result is invalid
        """
        try:
            print(f"Checking if result is valid and saving for search ID: {search_id}")
            
            # Extract price information
            price_details = self._extract_price_details(result)
            
            # Validate result using LLM
            validation_result = check_if_valid_search_result(
                query, 
                result['title'] + " - " + price_details
            )
            if not validation_result:
                return None
                
            print(f"Result is valid: {validation_result}")
            
            # Check for duplicate results
            if self._is_duplicate_result(search_id, validation_result['link']):
                return None
            
            # Save the result
            self._save_result(search_id, result, validation_result, url)
            return {"message": "Result saved successfully."}
            
        except Exception as e:
            print(f"Error while checking result: {e}")
            return {"error": "An error occurred while checking the result."}

    def _extract_price_details(self, result: Dict[str, Any]) -> str:
        """Extract price details from result data.
        
        Args:
            result: Product result data
            
        Returns:
            str: Formatted price details
        """
        if 'price' in result:
            return result['price']
        elif 'price_from' in result and 'price_to' in result:
            return f"from {result['price_from']} to {result['price_to']}"
        return ""

    def _is_duplicate_result(self, search_id: str, link: str) -> bool:
        """Check if a result with the same path already exists.
        
        Args:
            search_id: Search identifier
            link: Product link to check
            
        Returns:
            bool: True if duplicate found, False otherwise
        """
        results_data = self.redis_client.get(f"{search_id}:results")
        if results_data is None:
            return False
            
        try:
            results = json.loads(results_data.decode('utf-8'))
            result_paths = [urlparse(r['link']).path for r in results]
            return urlparse(link).path in result_paths
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False

    def _save_result(
        self, 
        search_id: str, 
        result: Dict[str, Any], 
        validation_result: Dict[str, Any], 
        url: str
    ):
        """Save a validated result to Redis.
        
        Args:
            search_id: Search identifier
            result: Original result data
            validation_result: Validated result data
            url: Source website URL
        """
        results_data = self.redis_client.get(f"{search_id}:results")
        if results_data is None:
            results = []
        else:
            try:
                results = json.loads(results_data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                results = []
        
        results.append({
            'title': validation_result['title'],
            'price': result.get('price'),
            'price_from': result.get('price_from'),
            'price_to': result.get('price_to'),
            'link': result['link'],
            'seller': url,
            'image': result.get('image'),
        })
        
        self.redis_client.set(f"{search_id}:results", json.dumps(results))
