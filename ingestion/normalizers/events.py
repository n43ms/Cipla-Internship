from __future__ import annotations

import re
import string
from typing import Any


MONTH_SUFFIX = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s*(20)?\d{0,2}\b$")


def normalize_event_name(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.lower().strip()
    text = re.sub(r"\((new|old|planned|actual)\)", " ", text)
    text = MONTH_SUFFIX.sub(" ", text)
    text = text.translate(str.maketrans({char: " " for char in string.punctuation}))
    return " ".join(text.split())

