import requests

HEADERS = {"User-Agent": "EMO_WRITER/1.0"}
BASE_URL = "https://www.reddit.com/r/{subreddit}/hot.json"


def fetch_hot_posts(subreddit: str, limit: int = 100) -> list[dict]:
    """
    Fetch hot posts from a subreddit using Reddit's public JSON API.
    No credentials required — just a User-Agent header.
    Returns the list of post data dicts.
    """
    url = BASE_URL.format(subreddit=subreddit)
    params = {"limit": limit, "raw_json": 1}
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    children = response.json()["data"]["children"]
    return [child["data"] for child in children]
