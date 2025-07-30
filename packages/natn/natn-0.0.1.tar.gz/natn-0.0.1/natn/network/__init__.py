from httpx import AsyncClient, RequestError

async def post(url: str, json: dict, timeout=900):
    async with AsyncClient() as client:
        try:
            response = await client.post(url, json=json, timeout=timeout)
            return {
                "instance": response,
                "status": response.status_code,
                "json": response.json()
            }
        except RequestError as e:
            #print(f"Request failed for {url}: {e}")
            return {
                "instance": None,
                "status": None,
                "json": None
            }

def is_valid_response(r):
    return r is not None and r.get("instance") is not None and r.get("status") == 200
