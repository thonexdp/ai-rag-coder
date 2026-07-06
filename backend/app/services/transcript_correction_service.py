from __future__ import annotations

import logging
from collections.abc import Callable

from app.core.config import get_settings


logger = logging.getLogger(__name__)

_CORRECTION_SYSTEM_PROMPT = """You are a speech transcription corrector for Filipino (Tagalog) and Cebuano (Bisaya) language.

Correct only speech recognition errors caused by pronunciation or accent.

Rules:
- Preserve the original meaning.
- Do not add new information.
- Do not answer the question.
- Do not translate between languages.
- Keep English technical terms (Flutter, Python, RAG, Ollama, API, SQL, etc.) unchanged.
- Correct common ASR mistakes such as "enge" -> "ng" only when appropriate from context.
- Add proper punctuation and capitalization.
- Return only the corrected transcript."""


class TranscriptCorrectionService:
    def __init__(
        self,
        text_generator: Callable[[list[dict[str, str]], float], str] | None = None,
    ) -> None:
        self.settings = get_settings()
        self._text_generator = text_generator or self._generate_text

    def correct_transcript(self, transcript: str, language: str | None) -> str:
        cleaned = transcript.strip()
        if not cleaned:
            return cleaned

        normalized_language = (language or "").lower().strip()
        if normalized_language not in {"fil", "ceb"}:
            return cleaned

        messages = [
            {"role": "system", "content": _CORRECTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n{cleaned}"},
        ]
        try:
            corrected = self._text_generator(messages, 0.0).strip()
            return corrected or cleaned
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.warning("Transcript correction failed, using original transcript: %s", exc)
            return cleaned

    def _generate_text(self, messages: list[dict[str, str]], temperature: float) -> str:
        provider = self.settings.llm_provider.lower().strip()
        if provider == "openai":
            return self._generate_with_openai(messages, temperature)
        if provider == "ollama":
            return self._generate_with_ollama(messages, temperature)
        raise ValueError(f"Unsupported LLM_PROVIDER: {self.settings.llm_provider}")

    def _generate_with_ollama(self, messages: list[dict[str, str]], temperature: float) -> str:
        from ollama import Client

        client = Client(host=self.settings.ollama_base_url)
        response = client.chat(
            model=self.settings.ollama_model,
            messages=messages,
            options={"temperature": temperature},
        )
        content = response["message"]["content"].strip()
        if not content:
            raise ValueError("Ollama returned an empty correction")
        return content

    def _generate_with_openai(self, messages: list[dict[str, str]], temperature: float) -> str:
        from openai import OpenAI

        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        if not self.settings.openai_model:
            raise ValueError("OPENAI_MODEL is required when LLM_PROVIDER=openai")

        client = OpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
            timeout=self.settings.openai_timeout_seconds,
        )
        completion = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=messages,
            temperature=temperature,
        )
        content = completion.choices[0].message.content or ""
        if not content.strip():
            raise ValueError("OpenAI returned an empty correction")
        return content.strip()
