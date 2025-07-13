from pydantic import BaseModel
from pydantic import BaseModel, Field
from openai import OpenAI
client = OpenAI()

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o", temperature=0)


class SearchInput(BaseModel):
    query: str

class MatchRequest(BaseModel):
    query: str
    result: str

class MatchResponse(BaseModel):
    match: bool


class QueryResultMatch:
    def __init__(self, prompt: str):
        self.prompt = prompt

    def check(self, req: MatchRequest) -> MatchResponse:
        prompt = f"""
        Query: {req.query}
        Result: {req.result}

        {self.prompt}
        """

        response = client.responses.create(
            model="gpt-4",  # or gpt-3.5-turbo
            input=prompt,
            temperature=0
        )

        answer = response.output_text.strip()
        match = answer.lower() == "true"
        return MatchResponse(match=match)


class YesNoMatch:
    def __init__(self, prompt: str):
        self.prompt = prompt

    def check(self, req: SearchInput) -> MatchResponse:
        prompt = f"""
        Query: {req.query}

        {self.prompt}
        """

        response = client.responses.create(
            model="gpt-4",  # or gpt-3.5-turbo
            input=prompt,
            temperature=0
        )

        answer = response.output_text.strip()
        match = answer.lower() == "true"
        return MatchResponse(match=match)