from __future__ import annotations

from typing import Any

import httpx

from core.error_handling.handlers import ToolError


class UXPilotClient:
    BASE_URL = "https://uxpilot.ai/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def generate_wireframe(self, prompt: str, screen_type: str = "desktop") -> dict[str, Any]:
        if not self.api_key:
            return {"error": "UXPILOT_API_KEY not configured", "prompt": prompt}
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    f"{self.BASE_URL}/wireframes",
                    headers=self._headers,
                    json={"prompt": prompt, "screen_type": screen_type},
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise ToolError(str(e), tool_name="uxpilot")

    def get_wireframe(self, wireframe_id: str) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(
                    f"{self.BASE_URL}/wireframes/{wireframe_id}",
                    headers=self._headers,
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise ToolError(str(e), tool_name="uxpilot")
