"""
The 'brain': sends transcribed speech to Claude and keeps a running
conversation history so replies stay coherent turn to turn.
"""
import anthropic

import config


class Conversation:
    def __init__(self):
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self._client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self._history = []  # list of {"role": ..., "content": ...}

    def respond(self, user_text: str) -> str:
        self._history.append({"role": "user", "content": user_text})

        response = self._client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=config.MAX_TOKENS,
            system=config.SYSTEM_PROMPT,
            messages=self._history,
        )

        reply_text = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

        self._history.append({"role": "assistant", "content": reply_text})
        return reply_text

    def reset(self):
        self._history = []
