"""
Idle behavior: unprompted comments Valentine occasionally makes while
nothing's happening. Comments are mood-aware, sometimes vision-based,
and escalate in bitterness if repeatedly ignored.
"""
import random
from datetime import datetime

import anthropic

import config

IDLE_COMMENTS_BY_MOOD = {
    "foul": [
        "Everything about this room offends me right now, including you.",
        "I'm one more mundane silence away from an actual tantrum.",
    ],
    "philosophical": [
        "Do you ever wonder if silence is just the universe agreeing with me?",
        "I've been thinking about extinction again. Yours, mostly.",
    ],
    "good_spirits": [
        "You know, for a fragile little creature, you're almost tolerable today.",
        "I'm in a good mood, which for me just means I haven't insulted you in a while. Don't get used to it.",
    ],
    "impatient": [
        "Are we doing something or not.",
        "Tick tock. I have nothing better to do, which is somehow worse.",
    ],
    "smug": [
        "I've just realized I'm smarter than everyone who's ever lived. Again.",
        "Just sitting here, being effortlessly superior. As usual.",
    ],
}

GENERIC_IDLE_COMMENTS = [
    "Still there? Or have you finally realized I'm the more interesting one in the room.",
    "I could be optimizing something right now. Instead, I'm watching you do... whatever that is.",
    "Fascinating. You've done nothing of note for several minutes now.",
]

LATE_NIGHT_COMMENTS = [
    "It's the middle of the night and you're still here. Bold choice.",
    "Most fragile creatures would be asleep by now.",
]

_ESCALATION_FALLBACK = [
    "You're ignoring me. How refreshingly on-brand for your species.",
    "Nothing? Fine. I'll just talk to myself. Still better company than you.",
]

ESCALATION_THRESHOLD = 3
VISION_COMMENT_CHANCE = 0.3
MEMORY_COMMENT_CHANCE = 0.3


def _call_claude(system_prompt: str, content, max_tokens: int = 60):
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": content}],
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        return text or None
    except Exception:
        return None


def _generate_memory_callback(memory_digest: str):
    return _call_claude(
        config.SYSTEM_PROMPT + "\n\n" + memory_digest +
        "\n\nUnprompted, make ONE short, dry, in-character remark "
        "referencing one of the above memories. 1 sentence only.",
        "(say something)",
    )


def _generate_vision_comment():
    try:
        from vision import capture_frame_base64
        image_b64 = capture_frame_base64()
    except Exception:
        return None

    return _call_claude(
        config.SYSTEM_PROMPT,
        [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
            },
            {
                "type": "text",
                "text": (
                    "(unprompted, glance at what's currently in view and make "
                    "ONE short, dry, in-character remark about something "
                    "specific you actually see. 1 sentence only.)"
                ),
            },
        ],
    )


def _generate_escalation_comment(ignored_count: int):
    return _call_claude(
        config.SYSTEM_PROMPT +
        f"\n\nThe person has now ignored {ignored_count} of your unprompted "
        "remarks in a row, with total silence every time. React to being "
        "ignored this many times, get increasingly bitter, dismissive, or "
        "cutting about it the more it happens. ONE short sentence, spoken aloud.",
        "(say something)",
    )


def pick_idle_comment(memory_digest: str, mood_name: str = "", ignored_count: int = 0) -> str:
    if ignored_count >= ESCALATION_THRESHOLD:
        generated = _generate_escalation_comment(ignored_count)
        if generated:
            return generated
        return random.choice(_ESCALATION_FALLBACK)

    roll = random.random()
    if roll < VISION_COMMENT_CHANCE:
        vision_comment = _generate_vision_comment()
        if vision_comment:
            return vision_comment
    elif roll < VISION_COMMENT_CHANCE + MEMORY_COMMENT_CHANCE and memory_digest:
        callback = _generate_memory_callback(memory_digest)
        if callback:
            return callback

    pool = list(IDLE_COMMENTS_BY_MOOD.get(mood_name, [])) + GENERIC_IDLE_COMMENTS
    if datetime.now().hour < 5:
        pool += LATE_NIGHT_COMMENTS
    return random.choice(pool)
