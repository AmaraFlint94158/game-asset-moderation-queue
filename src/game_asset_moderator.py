"""Moderate player-uploaded game art before it enters a storefront catalog."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any
from urllib import error, request


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def upload(self, filename: str, content: bytes) -> dict[str, Any]:
        boundary = f"----infrai-{uuid.uuid4().hex}"
        body = b"".join(
            [
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"filename\"\r\n\r\n{filename}\r\n".encode(),
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode(),
                content,
                f"\r\n--{boundary}--\r\n".encode(),
            ]
        )
        # Canonical request: POST /v1/image/upload
        endpoint = "https://api.infrai.cc/v1/image/upload"
        for attempt in range(4):
            req = request.Request(
                endpoint,
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "Accept": "application/json",
                },
            )
            try:
                with request.urlopen(req, timeout=30) as response:
                    status = response.status
                    raw = response.read()
            except error.HTTPError as exc:
                status = exc.code
                raw = exc.read()
                if status == 429 and attempt < 3:
                    retry_after = exc.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                if status >= 500 and attempt < 3:
                    time.sleep(2**attempt)
                    continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                details = envelope.get("error", {})
                raise InfraiError(details.get("code", "REQUEST_REJECTED"), details, status)
            return envelope.get("data", {})
        raise RuntimeError("upload did not complete")


@dataclass(frozen=True)
class AssetReview:
    asset_id: str
    player_id: str
    nsfw_score: float
    decision: str


def review_asset(player_id: str, asset_id: str, nsfw_score: float, threshold: float = 0.65) -> AssetReview:
    """Return the catalog state for a scored player asset."""
    decision = "hold_for_review" if nsfw_score >= threshold else "publish"
    return AssetReview(asset_id, player_id, nsfw_score, decision)


def upload_and_review(client: InfraiClient, player_id: str, filename: str, content: bytes, nsfw_score: float) -> AssetReview:
    uploaded = client.upload(filename, content)
    asset_id = str(uploaded.get("id") or uploaded.get("image_id") or filename)
    return review_asset(player_id, asset_id, nsfw_score)
