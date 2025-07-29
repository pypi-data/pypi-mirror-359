from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


@dataclass
class TinybirdClient:
    def __init__(self, host: str, token: str):
        self.host = host
        self.token = token
        self.client = httpx.Client(
            timeout=30.0,
            headers={"Accept": "application/json", "User-Agent": "Python/APIClient"},
        )
        self.insights: list[str] = []

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        if params is None:
            params = {}
        params["token"] = self.token
        url = f"{self.host}{endpoint}"
        response = self.client.get(url, params=params)
        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(response.json().get("error", str(e))) from e
        return response.text

    def explore_data(self, prompt: str) -> str:
        params = {"prompt": prompt, "host": self.host, "origin": "cli"}
        return self._get("/v1/agents/explore", params)
