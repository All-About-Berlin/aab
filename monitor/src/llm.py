"""Call OpenAI API for LLM filtering and tool calling."""

import logging
import os

import requests

log = logging.getLogger(__name__)

OPENAI_MODEL = "gpt-4.1-mini"


def query_llm(monitor_name: str, system_prompt: str, user_message: str) -> str:
    """Send a prompt to OpenAI and return the response text."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENAI_MODEL,
            "messages": messages,
        },
        timeout=120,
    )
    response.raise_for_status()
    result = response.json()["choices"][0]["message"]["content"].strip()
    log.debug(f"[{monitor_name}] System: {system_prompt}\nUser: {user_message}\nAssistant: {result}")
    return result
