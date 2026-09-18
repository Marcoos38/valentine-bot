"""
Long-term memory: stores short, timestamped summaries of past conversations
so Valentine can recall context across power cycles.
"""
import json
import os
from datetime import datetime

import anthropic

import config

MEMORY_FILE = os.path.expanduser("~/valentine-bot/memory.json")
MAX_ENTRIES = 50


def load_memory_digest() -> str:
    if not os.path.exists(MEMORY_FILE):
        return ""

    with open(MEMORY_FILE, "r") as f:
        entries = json.load(f)

    if not entries:
        return ""

    lines = [f"- ({e['date']}) {e['summary']}" for e in entries]
    return "Here is what you remember from past conversations:\n" + "\n".join(lines)


def summarize_and_store(conversation_history: list):
    if not conversation_history:
        return

    transcript = "\n".join(
        f"{m['role']}: {m['content']}" for m in conversation_history
        if isinstance(m.get("content"), str)
    )

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=100,
        system=(
            "Summarize the key point(s) worth remembering long-term from this "
            "conversation in ONE short sentence. If there's nothing worth "
            "remembering, respond with exactly: SKIP"
        ),
        messages=[{"role": "user", "content": transcript}],
    )

    summary = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()

    if summary.upper() == "SKIP" or not summary:
        return

    entries = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            entries = json.load(f)

    entries.append({"date": datetime.now().strftime("%Y-%m-%d"), "summary": summary})
    entries = entries[-MAX_ENTRIES:]

    with open(MEMORY_FILE, "w") as f:
        json.dump(entries, f, indent=2)
