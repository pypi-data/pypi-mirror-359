import httpx

def fetch_json(url: str, headers: dict = None):
    response = httpx.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
