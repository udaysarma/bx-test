from pydantic import BaseModel, Field
from openai import OpenAI
client = OpenAI()

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o", temperature=0)

class MatchRequest(BaseModel):
    query: str
    search_result: str

class MatchResponse(BaseModel):
    match: bool

class SearchInput(BaseModel):
    path_data: str


def is_search_input(req: SearchInput) -> MatchResponse:
    prompt = f"""
    Query: {req.path_data}
    
    Given CSS path and other html input tag data, tell me if it's a search box of a website? Answer only with "True" or "False".
    """

    response = client.responses.create(
        model="gpt-4",  # or gpt-3.5-turbo
        input=prompt,
        temperature=0
    )

    answer = response.output_text.strip()
    match = answer.lower() == "true"
    return MatchResponse(match=match)


class SearchResult(BaseModel):
    title: str
    price: str
    link: str


def check_match(req: MatchRequest) -> MatchResponse:
    prompt = f"""
    Query: {req.query}
    Search Result: {req.search_result}
    
    Does the search result match the intent of the query? Answer only with "True" or "False".
    """

    response = client.responses.create(
        model="gpt-4",  # or gpt-3.5-turbo
        input=prompt,
        temperature=0
    )

    answer = response.output_text.strip()
    match = answer.lower() == "true"
    return MatchResponse(match=match)


class SearchResultFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    is_valid_search_result: bool = Field(description="Whether the search result matches the user's query. If it matches, return True, else False. If the search result is not valid, do not return the title, price and link.")
    title: str = Field(description="Exact title of the product without any extra information.")
    price: str = Field(description="price of the product")
    link: str = Field(description="The link to the product")

model_with_tools = model.bind_tools([SearchResultFormatter])

def check_if_valid_search_result(query: str, search_result: str):
    print(f"This is the query --- '{query}' --- does the given product match the query according to the title --- {search_result}")
    ai_msg = model_with_tools.invoke(f"This is the query --- '{query}' --- does the given product match the query according to the title --- {search_result}")
    if ai_msg.tool_calls and len(ai_msg.tool_calls) > 0:
        args = ai_msg.tool_calls[0]['args']
        if args['is_valid_search_result']:
            return args
    return None

def check_if_link_is_a_pagination_link(link: str) -> bool:
    """
    Check if the given link is a pagination link.
    """
    pagination_keywords = ['page', 'p=', 'page=', 'start=', 'offset=']
    return any(keyword in link for keyword in pagination_keywords)

