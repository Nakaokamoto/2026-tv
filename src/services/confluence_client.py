from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class ConfluencePage:
    page_id: str
    title: str
    version: int
    body_storage: str


class ConfluenceClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({"Content-Type": "application/json"})

    def get_page(self, page_id: str) -> ConfluencePage:
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {"expand": "body.storage,version"}
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        return ConfluencePage(
            page_id=page_id,
            title=payload["title"],
            version=payload["version"]["number"],
            body_storage=payload["body"]["storage"]["value"],
        )

    def update_page(self, page: ConfluencePage, new_body_storage: str) -> None:
        url = f"{self.base_url}/rest/api/content/{page.page_id}"
        payload = {
            "id": page.page_id,
            "type": "page",
            "title": page.title,
            "version": {"number": page.version + 1},
            "body": {"storage": {"value": new_body_storage, "representation": "storage"}},
        }
        response = self.session.put(url, json=payload, timeout=30)
        response.raise_for_status()
