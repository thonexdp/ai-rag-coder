from __future__ import annotations

import logging

from app.core.config import get_settings
from app.services.interfaces import LLMService


logger = logging.getLogger(__name__)


def _fallback_message(language: str, provider_label: str) -> str:
    if language == "fil":
        return (
            f"Pasensya na, hindi ko maabot ang {provider_label} ngayon. "
            "Heto ang pinakamalapit na sagot mula sa available na context."
        )
    if language == "ceb":
        return (
            f"Pasayloa, dili nako ma-access ang {provider_label} karon. "
            "Mao ni ang pinakaduol nga tubag gikan sa available nga context."
        )
    return f"I could not reach the {provider_label} just now, so here is the closest answer from the available context."


class OllamaLLMService(LLMService):
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_answer(self, prompt: str, language: str) -> str:
        try:
            from ollama import Client

            client = Client(host=self.settings.ollama_base_url)
            response = client.chat(
                model=self.settings.ollama_model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2},
            )
            return response["message"]["content"].strip()
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.warning("Ollama call failed, using prompt-context fallback: %s", exc)
            return _fallback_message(language, "local model")


class OpenAILLMService(LLMService):
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        if not self.settings.openai_model:
            raise ValueError("OPENAI_MODEL is required when LLM_PROVIDER=openai")

    def generate_answer(self, prompt: str, language: str) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                timeout=self.settings.openai_timeout_seconds,
            )
            try:
                response = client.responses.create(
                    model=self.settings.openai_model,
                    input=prompt,
                )
                output_text = getattr(response, "output_text", "") or ""
                if output_text.strip():
                    return output_text.strip()
                logger.warning("OpenAI responses API returned no output_text, falling back to chat completions")
            except Exception as exc:
                logger.warning("OpenAI responses API failed, falling back to chat completions: %s", exc)

            completion = client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            message = completion.choices[0].message.content or ""
            if message.strip():
                return message.strip()
            raise ValueError("OpenAI returned an empty completion")
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.warning("OpenAI call failed, using prompt-context fallback: %s", exc)
            return _fallback_message(language, "OpenAI model")


def get_llm_service() -> LLMService:
    settings = get_settings()
    provider = settings.llm_provider.lower().strip()
    if provider == "openai":
        return OpenAILLMService()
    if provider == "ollama":
        return OllamaLLMService()
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
