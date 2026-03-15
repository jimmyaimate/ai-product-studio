from __future__ import annotations

from typing import Any

import httpx

from core.error_handling.handlers import ToolError


class FigmaClient:
    BASE_URL = "https://api.figma.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._headers = {"X-Figma-Token": api_key}

    def get_file(self, file_key: str) -> dict[str, Any]:
        if not self.api_key:
            return {"error": "FIGMA_API_KEY not configured"}
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(f"{self.BASE_URL}/files/{file_key}", headers=self._headers)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise ToolError(str(e), tool_name="figma")

    def get_images(self, file_key: str, node_ids: list[str], format: str = "png") -> dict[str, Any]:
        if not self.api_key:
            return {"error": "FIGMA_API_KEY not configured"}
        try:
            ids_param = ",".join(node_ids)
            with httpx.Client(timeout=60) as client:
                resp = client.get(
                    f"{self.BASE_URL}/images/{file_key}",
                    headers=self._headers,
                    params={"ids": ids_param, "format": format},
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise ToolError(str(e), tool_name="figma")

    def export_component_specs(self, file_key: str) -> dict[str, Any]:
        file_data = self.get_file(file_key)
        # Extract component names and properties from the Figma file structure
        components = file_data.get("components", {})
        return {
            "file_key": file_key,
            "component_count": len(components),
            "components": {k: {"name": v.get("name"), "description": v.get("description", "")} for k, v in components.items()},
        }
