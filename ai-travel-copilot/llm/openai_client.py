from dotenv import load_dotenv
import json
import os
import re
from typing import Any, Dict

import requests

from llm.base_client import BaseLLMClient

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _extract_json_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for idx in range(start, len(text)):
        ch = text[idx]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]

    return None


class OpenAIClient(BaseLLMClient):
    """Kimi client via Moonshot OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "moonshot-v1-8k",
        base_url: str = "https://api.moonshot.cn/v1",
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY", "sk-wHYNR9gfO0n97vGsqxxLhleEylZlpOJ6RrFI5lC17SLtiwri").strip()
        self.model = os.getenv("MOONSHOT_MODEL", model).strip() or model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.use_env_proxy = _as_bool(os.getenv("MOONSHOT_USE_ENV_PROXY"), False)

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("Missing MOONSHOT_API_KEY in environment variables.")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个旅行规划助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        session = requests.Session()
        session.trust_env = self.use_env_proxy
        try:
            resp = session.post(url, headers=headers, json=payload, timeout=self.timeout)
        except requests.exceptions.ProxyError as exc:
            raise RuntimeError(
                "Moonshot request failed due to proxy connection error. "
                "Set MOONSHOT_USE_ENV_PROXY=false to bypass system proxy, "
                "or fix HTTP(S)_PROXY configuration."
            ) from exc

        if not resp.ok:
            response_text = resp.text.strip()
            if len(response_text) > 1000:
                response_text = response_text[:1000] + "..."
            raise RuntimeError(
                f"Moonshot request failed with status {resp.status_code}: {response_text}"
            )

        data = resp.json()

        choices = data.get("choices", [])
        if not choices:
            raise ValueError(f"Invalid Moonshot response: {data}")

        return choices[0]["message"]["content"].strip()

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        text = self.generate(prompt)
        fenced = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
        raw = fenced.group(1) if fenced else _extract_json_object(text) or text

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            snippet = raw.strip()
            if len(snippet) > 1200:
                snippet = snippet[:1200] + "..."
            raise ValueError(f"Failed to parse model JSON output: {exc}. Raw output: {snippet}") from exc

        if not isinstance(parsed, dict):
            raise ValueError(f"Model JSON output must be an object, got: {type(parsed).__name__}")

        return parsed
