from helpers.llm import YesNoMatch, SearchInput
import json


"""
Given a form and its inputs in json parsed format, tells me if it's a search box of a website.
"""
def is_search_form(form: dict) -> bool:
    is_search_form = YesNoMatch(prompt="""
    Given a form and its inputs in json parsed format, tell me if it's a search box of a website? Answer only with "True" or "False".
    """)
    return is_search_form.check(SearchInput(query=json.dumps(form))).match


"""
Given an input in json parsed format, tells me if it's a search input of a website.
"""
def is_search_input(input: dict) -> bool:
    is_search_input = YesNoMatch(prompt="""
    Given an input in json parsed format, tell me if it's a search input of a website? Answer only with "True" or "False".
    """)
    return is_search_input.check(SearchInput(query=json.dumps(input))).match
