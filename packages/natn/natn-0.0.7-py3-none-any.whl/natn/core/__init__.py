import httpx

from ..config import API_URLS, API_NAMES
from ..network import post, is_valid_response
from ..package_manager import is_pip_package_installed, install_pip_package_anon

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


    if not is_pip_package_installed("g4f"):
        install_pip_package_anon("g4f")
        install_pip_package_anon("nodriver")
        install_pip_package_anon("curl_cffi")

    if is_pip_package_installed("g4f"):
        from g4f.client import AsyncClient
        client = AsyncClient()

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            web_search=False
        )

        message = response.choices[0].message.content

        if message is not None:
            return message

    return ""
