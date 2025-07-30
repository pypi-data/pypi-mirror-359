"""HTTP client for the Recallio API."""
from __future__ import annotations

import requests
from dataclasses import replace

from .models import (
    MemoryWriteRequest,
    MemoryRecallRequest,
    MemoryDeleteRequest,
    MemoryDto,
    MemoryWithScoreDto,
)
from .errors import RecallioAPIError


class RecallioClient:
    """Client for interacting with the Recallio API."""

    def __init__(self, api_key: str, base_url: str = "https://app.recallio.ai") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, json=json)
        if response.status_code >= 200 and response.status_code < 300:
            if response.content:
                return response.json()
            return {}
        try:
            data = response.json()
            message = data.get("error", response.text)
        except ValueError:
            message = response.text
        raise RecallioAPIError(message, status_code=response.status_code)

    def write_memory(self, request: MemoryWriteRequest) -> MemoryDto:
        data = self._request("POST", "/api/Memory/write", json=request.to_dict())
        return MemoryDto(**data)

    def recall_memory(self, request: MemoryRecallRequest) -> list[MemoryWithScoreDto]:
        data = self._request("POST", "/api/Memory/recall", json=request.to_dict())
        if isinstance(data, list):
            return [MemoryWithScoreDto(**item) for item in data]
        return [MemoryWithScoreDto(**data)]

    def recall_summary(self, request: MemoryRecallRequest) -> MemoryWithScoreDto:
        """Helper to recall a single summarized memory."""
        summarized_req = replace(request, summarized=True)
        results = self.recall_memory(summarized_req)
        return results[0] if results else MemoryWithScoreDto()

    def delete_memory(self, request: MemoryDeleteRequest) -> None:
        self._request("POST", "/api/Memory/delete", json=request.to_dict())
        return None
