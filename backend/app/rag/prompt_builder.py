from app.schemas.chat import ChatSource


def build_prompt(
    question: str,
    language: str,
    document_sources: list[ChatSource],
    structured_context: str | None,
    chat_memory: list[str],
) -> str:
    memory_text = "\n".join(chat_memory) if chat_memory else "No prior chat history."
    source_blocks = [
        f"- {source.title}: {source.snippet}" + (f" (page {source.page})" if source.page else "")
        for source in document_sources
    ]
    sources_text = "\n".join(source_blocks) if source_blocks else "No document context available."
    structured_text = structured_context or "No structured data available."
    language_instruction = {
        "fil": "Respond in Filipino/Tagalog when possible.",
        "ceb": "Respond in Bisaya/Cebuano when possible.",
        "en": "Respond in English.",
    }.get(language, "Respond in the user's language.")

    return f"""
You are an AI School Assistant. Use only the provided context. If the context is missing, say you do not have enough information.
{language_instruction}
Always prefer factual, concise answers. Mention sources when citing documents.

Recent chat history:
{memory_text}

Structured school data:
{structured_text}

Document context:
{sources_text}

Question:
{question}
""".strip()
