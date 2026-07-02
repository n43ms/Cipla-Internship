from __future__ import annotations

import re
import string
from typing import Any

MONTH_SUFFIX = re.compile(
    r"(\b|-|_)\s*"
    r"(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|"
    r"sep|sept|september|oct|october|nov|november|dec|december)"
    r"\s*('?\d{2}|20\d{2})?\s*$"
)


def normalize_event_name(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.lower().strip()
    text = re.sub(r"\((new|old|planned|actual|activity)\)", " ", text)
    text = re.sub(r"\b(new|old|planned|actual)\s+activity\b", " ", text)
    text = text.strip()
    text = MONTH_SUFFIX.sub(" ", text)
    text = text.translate(str.maketrans({char: " " for char in string.punctuation}))
    return " ".join(text.split())
