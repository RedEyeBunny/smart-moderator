from app.config import settings

from typing import Literal


Classification = Literal["toxic", "spam", "harassment", "safe"]


BAD_WORDS = {"idiot", "stupid", "hate", "kill"}
SPAM_HINTS = {"free money", "click here", "buy now", "visit my profile"}
HARASSMENT_HINTS = {"you are worthless", "go away", "shut up"}


def heuristic_classify_text(text: str) -> tuple[Classification, float, str]:
    t = text.lower()
    score = 0.5
    reasons = []
    if any(p in t for p in SPAM_HINTS):
        reasons.append("spam phrase detected")
        return ("spam", 0.9, "; ".join(reasons))
    if any(w in t for w in BAD_WORDS):
        reasons.append("toxic word detected")
        return ("toxic", 0.85, "; ".join(reasons))
    if any(p in t for p in HARASSMENT_HINTS):
        reasons.append("harassment phrase detected")
        return ("harassment", 0.8, "; ".join(reasons))
    return ("safe", 0.95, "no issues found")


import json
import os
import requests


OPENAI_URL = "https://api.openai.com/v1/chat/completions"


PROMPT = (
    "You are a content moderation assistant. Classify the user content into one of: "
    "toxic, spam, harassment, safe. Return strict JSON with keys: classification, "
    "confidence (0-1 float), reasoning (short)."
)


def openai_classify_text(text: str) -> tuple[Classification, float, str, str]:
    api_key = settings.OPENAI_API_KEY
    model = settings.OPENAI_MODEL
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    try:
        parsed = json.loads(content)
        return (
            parsed.get("classification", "safe"),
            float(parsed.get("confidence", 0.9)),
            parsed.get("reasoning", ""),
            json.dumps(data),
        )
    except Exception:
        return "safe", 0.5, "LLM parse error; defaulting to safe", json.dumps(data)


def classify_text(text: str):
    if settings.OPENAI_API_KEY:
        try:
            c, conf, reason, raw = openai_classify_text(text)
            return c, conf, reason, raw
        except Exception as e:
            c, conf, reason = heuristic_classify_text(text)
            return c, conf, reason, f"openai_error={e}"
        else:
            c, conf, reason = heuristic_classify_text(text)
            return c, conf, reason, "no_llm_key_heuristic_used"
