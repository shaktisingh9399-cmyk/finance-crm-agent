"""LLM provider selection with Groq → Gemini → Ollama failover."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from django.conf import settings

from agent_core.enums import (
    HttpContentType,
    HttpHeader,
    HttpMethod,
    LLMProvider,
    LLMRequestKey,
    MessageField,
    ToolCallField,
    ToolChoice,
)

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.0-flash-exp"
OLLAMA_MODEL = getattr(settings, "OLLAMA_MODEL", "llama3")


@dataclass
class LLMResponse:
    """Normalized LLM completion response."""

    content: str
    provider: str
    tool_calls: list[dict[str, Any]]


class BaseLLMClient(ABC):
    """Abstract LLM client interface."""

    provider: str

    @abstractmethod
    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        """Run a chat completion with optional tool definitions."""


class GroqClient(BaseLLMClient):
    provider = LLMProvider.GROQ.value

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=tools or None,
            tool_choice=ToolChoice.AUTO.value if tools else None,
        )
        choice = response.choices[0].message
        tool_calls = []
        if choice.tool_calls:
            for tc in choice.tool_calls:
                tool_calls.append(
                    {
                        ToolCallField.ID.value: tc.id,
                        ToolCallField.NAME.value: tc.function.name,
                        ToolCallField.ARGUMENTS.value: tc.function.arguments,
                    }
                )
        return LLMResponse(
            content=choice.content or "",
            provider=self.provider,
            tool_calls=tool_calls,
        )


class GeminiClient(BaseLLMClient):
    provider = LLMProvider.GEMINI.value

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = "\n".join(
            f"{m[MessageField.ROLE.value]}: {m[MessageField.CONTENT.value]}" for m in messages
        )
        response = model.generate_content(prompt)
        return LLMResponse(
            content=response.text or "",
            provider=self.provider,
            tool_calls=[],
        )


class OllamaClient(BaseLLMClient):
    provider = LLMProvider.OLLAMA.value

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        import json
        import urllib.request

        payload = json.dumps(
            {
                LLMRequestKey.MODEL.value: OLLAMA_MODEL,
                LLMRequestKey.MESSAGES.value: messages,
                LLMRequestKey.STREAM.value: False,
            }
        ).encode()
        req = urllib.request.Request(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            data=payload,
            headers={HttpHeader.CONTENT_TYPE.value: HttpContentType.JSON.value},
            method=HttpMethod.POST.value,
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        return LLMResponse(
            content=data.get(MessageField.MESSAGE.value, {}).get(MessageField.CONTENT.value, ""),
            provider=self.provider,
            tool_calls=[],
        )


class LLMSelector:
    """Select an available LLM client with automatic provider failover."""

    _PROVIDERS: list[type[BaseLLMClient]] = [GroqClient, GeminiClient, OllamaClient]

    def get_client(self) -> BaseLLMClient:
        """
        Return the first healthy LLM client.

        Returns:
            BaseLLMClient instance for the selected provider.

        Raises:
            RuntimeError: If no provider is configured.
        """
        last_error: Optional[Exception] = None
        for client_cls in self._PROVIDERS:
            if not self._is_configured(client_cls):
                continue
            try:
                client = client_cls()
                logger.info("LLM provider selected: %s", client.provider)
                return client
            except Exception as exc:
                last_error = exc
                logger.warning("LLM provider %s unavailable: %s", client_cls.provider, exc)
        raise RuntimeError(f"No LLM provider available: {last_error}")

    def complete_with_failover(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMResponse:
        """Try each configured provider in order until one succeeds."""
        last_error: Optional[Exception] = None
        for client_cls in self._PROVIDERS:
            if not self._is_configured(client_cls):
                continue
            try:
                client = client_cls()
                response = client.complete(messages, tools)
                logger.info("LLM completion via provider=%s", response.provider)
                return response
            except Exception as exc:
                last_error = exc
                status = getattr(exc, "status_code", None)
                if status == 429:
                    logger.warning("Rate limit on %s — failing over", client_cls.provider)
                else:
                    logger.warning("LLM error on %s: %s", client_cls.provider, exc)
        raise RuntimeError(f"All LLM providers failed: {last_error}")

    @staticmethod
    def _is_configured(client_cls: type[BaseLLMClient]) -> bool:
        if client_cls is GroqClient:
            return bool(settings.GROQ_API_KEY)
        if client_cls is GeminiClient:
            return bool(settings.GEMINI_API_KEY)
        return bool(settings.OLLAMA_BASE_URL)
