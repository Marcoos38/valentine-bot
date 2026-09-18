"""
The 'brain': sends transcribed speech to Claude, letting Claude decide on
its own when to use the eye camera via tool use, rather than fixed trigger phrases.
"""
import anthropic

import config
from memory import load_memory_digest

LOOK_TOOL = {
    "name": "look",
    "description": (
        "Capture what is currently visible through your eye camera. Use this "
        "whenever actually seeing the room, the person, or an object would "
        "let you answer more accurately or add real, specific detail, not "
        "just when directly asked to look."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


class Conversation:
    def __init__(self, mood_modifier: str = ""):
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self._client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self._history = []
        self._memory_digest = load_memory_digest()
        self._mood_modifier = mood_modifier

    def _build_system_prompt(self) -> str:
        prompt = config.SYSTEM_PROMPT
        if self._mood_modifier:
            prompt += "\n\n" + self._mood_modifier
        if self._memory_digest:
            prompt += "\n\n" + self._memory_digest
        return prompt

    def respond(self, user_text: str, capture_frame_fn=None) -> str:
        self._history.append({"role": "user", "content": user_text})
        tools = [LOOK_TOOL] if capture_frame_fn else []

        response = self._client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=config.MAX_TOKENS,
            system=self._build_system_prompt(),
            messages=self._history,
            tools=tools,
        )

        if response.stop_reason == "tool_use" and capture_frame_fn:
            tool_use_block = next(b for b in response.content if b.type == "tool_use")
            self._history.append({"role": "assistant", "content": response.content})

            try:
                image_b64 = capture_frame_fn()
                tool_result_content = [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    }
                ]
            except Exception:
                tool_result_content = "Camera capture failed."

            self._history.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": tool_result_content,
                        }
                    ],
                }
            )

            response = self._client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=config.MAX_TOKENS,
                system=self._build_system_prompt(),
                messages=self._history,
                tools=tools,
            )

        reply_text = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

        self._history.append({"role": "assistant", "content": reply_text})
        return reply_text

    def get_history(self):
        return self._history

    def reset(self):
        self._history = []
