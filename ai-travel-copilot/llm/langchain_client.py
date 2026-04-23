from __future__ import annotations

import json
from typing import Any, Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from config.settings import settings
from llm.mock_client import MockLLMClient
from llm.openai_client import OpenAIClient


class LangChainChatModel(BaseChatModel):
    """Lightweight LangChain chat model adapter over existing clients."""

    provider: str = settings.LANGCHAIN_LLM_PROVIDER

    @property
    def _llm_type(self) -> str:
        return f"langchain_{self.provider}"

    def _get_backend(self):
        if self.provider == "openai":
            return OpenAIClient()
        return MockLLMClient()

    def _serialize_messages(self, messages: Sequence[BaseMessage]) -> str:
        parts: list[str] = []
        for message in messages:
            role = "user"
            if isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, HumanMessage):
                role = "user"
            parts.append(f"[{role}] {message.content}")
        return "\n".join(parts)

    def _generate(
        self,
        messages: Sequence[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        backend = self._get_backend()
        prompt = self._serialize_messages(messages)
        content = backend.generate(prompt)
        if stop:
            for token in stop:
                if token and token in content:
                    content = content.split(token)[0]
                    break
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    def invoke_text(self, prompt: str, system_prompt: str = "你是一个旅行规划助手。") -> str:
        result = self.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
        ])
        return str(result.content)

    def invoke_json(self, prompt: str, system_prompt: str = "你是一个旅行规划助手。") -> dict[str, Any]:
        text = self.invoke_text(prompt=prompt, system_prompt=system_prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start : end + 1])
            raise
