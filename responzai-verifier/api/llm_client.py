# api/llm_client.py
# Zentraler AsyncAnthropic-Client mit Retry-Logik fuer 429 Rate Limit Errors.
# Alle Agenten importieren von hier statt eigene Clients zu erstellen.

import asyncio
import anthropic
from pipeline.config import LLM_MODEL, LLM_MODEL_STRONG

client = anthropic.AsyncAnthropic()

MAX_RETRIES = 5
INITIAL_BACKOFF = 5  # Sekunden


async def call_llm(
    system: str,
    user_message: str,
    model: str = None,
    max_tokens: int = 2048,
    temperature: float = 0,
) -> str:
    """
    Ruft Claude auf mit automatischem Retry bei 429 Rate Limit Errors.

    Exponential Backoff: 5s, 10s, 20s, 40s, 80s
    Gibt den Text-Content der Antwort zurueck.
    """
    if model is None:
        model = LLM_MODEL

    for attempt in range(MAX_RETRIES):
        try:
            message = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text
        except anthropic.RateLimitError as e:
            if attempt < MAX_RETRIES - 1:
                wait = INITIAL_BACKOFF * (2 ** attempt)
                print(f"Rate limit hit (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait}s...")
                await asyncio.sleep(wait)
            else:
                raise
        except anthropic.APIStatusError as e:
            if e.status_code == 529:  # Overloaded
                if attempt < MAX_RETRIES - 1:
                    wait = INITIAL_BACKOFF * (2 ** attempt)
                    print(f"API overloaded (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    raise
            else:
                raise
