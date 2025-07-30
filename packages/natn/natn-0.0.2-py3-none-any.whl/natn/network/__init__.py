from httpx import AsyncClient, RequestError, DecodingError

async def post(url: str, json: dict, timeout=900):
    async with AsyncClient() as client:
        try:
            response = await client.post(url, json=json, timeout=timeout)
            try:
                json_data = response.json()
            except DecodingError:
                json_data = None
            except Exception:
                json_data = None
            return {
                "instance": response,
                "status": response.status_code,
                "json": json_data
            }
        except RequestError:
            return {
                "instance": None,
                "status": None,
                "json": None
            }

def is_valid_response(r):
    return r is not None and r.get("instance") is not None and r.get("status") == 200
