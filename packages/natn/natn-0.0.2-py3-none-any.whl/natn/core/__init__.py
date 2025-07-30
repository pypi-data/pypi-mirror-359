import httpx

from ..config import API_URLS, API_NAMES
from ..network import post, is_valid_response

async def ask(question: str, python_only: bool):
    payload = {
        "question": question,
        "python_only": python_only,
        "subject": "fisica"
    }

    for i, url in enumerate(API_URLS):
        response = await post(url, payload)
        if is_valid_response(response):
            response_json = response.get("json", None)
            raw_answer = response_json.get("answer", None)
            if raw_answer is not None:
                return raw_answer

    
    return ""
