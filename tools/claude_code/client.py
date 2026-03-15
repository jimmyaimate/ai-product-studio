from __future__ import annotations

import subprocess
import shutil
from pathlib import Path
from typing import Any

from core.error_handling.handlers import ToolError


class ClaudeCodeClient:
    """Wrapper to invoke the `claude` CLI for code generation tasks."""

    def __init__(self, working_dir: str | Path | None = None):
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()

    def _find_claude_binary(self) -> str | None:
        return shutil.which("claude")

    def is_available(self) -> bool:
        return self._find_claude_binary() is not None

    def run_prompt(self, prompt: str, timeout: int = 120) -> dict[str, Any]:
        binary = self._find_claude_binary()
        if not binary:
            return {
                "available": False,
                "prompt": prompt,
                "message": "claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code",
            }
        try:
            result = subprocess.run(
                [binary, "--print", prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.working_dir),
            )
            return {
                "available": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            raise ToolError(f"claude CLI timed out after {timeout}s", tool_name="claude_code")
        except Exception as e:
            raise ToolError(str(e), tool_name="claude_code")

    def generate_feature(self, feature_description: str, project_path: str | Path) -> dict[str, Any]:
        prompt = (
            f"You are building a software feature. Working directory: {project_path}\n\n"
            f"Feature to implement:\n{feature_description}\n\n"
            "Implement this feature with proper error handling, tests, and documentation."
        )
        return self.run_prompt(prompt)
