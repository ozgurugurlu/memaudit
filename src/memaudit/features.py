"""Typography normalisation, markdown stripping and the QUERY-BLIND session/turn feature set of the Part A audit.

Query-blindness is structural: every function here takes only the text/turns of ONE unit (plus an optional position scalar that the caller passes explicitly
and that is NOT part of the primary feature set).  Nothing here can see a question, an id, a label or another unit.

Feature groups (fixed in advance, the original audit protocol): typography (T), format (F), length (L), lexical-style (X).  The lexical group is computed on typography-normalised
text on purpose, so typographic differences live ONLY in group T and the pre-declared fixes remove exactly what they claim to remove.
"""
from __future__ import annotations

import math
import re
import unicodedata
from typing import Sequence

# ---------------------------------------------------------------------------------------------------------------------------------
# F1: typography normalisation (deterministic, idempotent, letters/digits untouched, accents kept)
# ---------------------------------------------------------------------------------------------------------------------------------
_SANITIZE_MAP = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'", "ʼ": "'", "′": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"', "″": '"', "«": '"', "»": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "−": "-", "⁃": "-",
    "—": " - ", "―": " - ",
    "…": "...",
    "•": "-", "●": "-", "·": "-",
    "→": "->", "←": "<-",
    " ": " ", " ": " ", " ": " ", " ": " ", " ": " ", " ": " ", " ": " ", " ": " ", " ": " ", " ": " ",
    " ": " ", " ": " ", " ": " ", " ": " ", "　": " ",
    "​": "", "‌": "", "‍": "", "⁠": "", "﻿": "", "️": "",
}
_SANITIZE_TABLE = str.maketrans(_SANITIZE_MAP)
_MULTISPACE = re.compile(r"[ \t]{2,}")


def sanitize_text(text: str) -> str:
    """F1.  Normalise typographic punctuation (U+2019 and friends), dashes, ellipsis, bullets, odd spaces; newlines kept; blank runs collapse to one space."""
    if not isinstance(text, str):
        raise TypeError("sanitize_text expects str")
    out = text.translate(_SANITIZE_TABLE)
    out = unicodedata.normalize("NFC", out)
    return _MULTISPACE.sub(" ", out)


# ---------------------------------------------------------------------------------------------------------------------------------
# F2: F1 + markdown formatting stripped (bold/italic markers, headers, list markers, fences, rules)
# ---------------------------------------------------------------------------------------------------------------------------------
_MD_BOLD = re.compile(r"\*\*([^*\n]+)\*\*")
_MD_UNDER = re.compile(r"__([^_\n]+)__")
_MD_HEADER = re.compile(r"(?m)^\s{0,3}#{1,6}\s+")
_MD_BULLET = re.compile(r"(?m)^\s*(?:[-*•]|\d{1,2}[.)])\s+")
_MD_FENCE = re.compile(r"```[a-zA-Z0-9_+-]*")
_MD_RULE = re.compile(r"(?m)^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
_MD_TICKS = re.compile(r"`([^`\n]+)`")
_MD_ITALIC = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])")


def strip_markdown(text: str) -> str:
    out = _MD_FENCE.sub("", text)
    out = _MD_BOLD.sub(r"\1", out)
    out = _MD_UNDER.sub(r"\1", out)
    out = _MD_ITALIC.sub(r"\1", out)
    out = _MD_TICKS.sub(r"\1", out)
    out = _MD_HEADER.sub("", out)
    out = _MD_RULE.sub("", out)
    out = _MD_BULLET.sub("", out)
    return re.sub(r"\n{3,}", "\n\n", out)


def apply_fix(text: str, level: str) -> str:
    """level in {'raw', 'F1', 'F2'} (raw, F1 or F2)."""
    if level == "raw":
        return text
    if level == "F1":
        return sanitize_text(text)
    if level == "F2":
        return strip_markdown(sanitize_text(text))
    raise ValueError(f"unknown fix level {level!r}")


# ---------------------------------------------------------------------------------------------------------------------------------
# features
# ---------------------------------------------------------------------------------------------------------------------------------
FEATURE_GROUPS = {
    "typography": ["curly_apos", "curly_quote", "dash_typo", "ellipsis", "nonascii", "emoji", "straight_apos"],
    "format": ["md_bold", "md_header", "md_bullet", "code_fence", "newline", "url", "paren", "colon", "question", "exclaim"],
    "length": ["log_chars", "n_turns", "user_mean_chars", "other_mean_chars", "max_turn_chars", "user_char_share"],
    "lexical": ["mean_word_len", "ttr", "digit_rate", "upper_rate", "first_person", "second_person", "contraction", "mean_sent_len"],
}
FEATURE_NAMES = [f for g in FEATURE_GROUPS.values() for f in g]
FEATURE_INDEX = {n: i for i, n in enumerate(FEATURE_NAMES)}
GROUP_INDEX = {g: [FEATURE_INDEX[f] for f in fs] for g, fs in FEATURE_GROUPS.items()}
POSITION_FEATURES = ["rel_pos", "log_n_units"]            # NOT part of the style set; used only by the separate position-only probe

_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
_URL = re.compile(r"https?://\S+")
_WORD = re.compile(r"[a-z0-9']+")
_SENT = re.compile(r"[.!?]+")
_FIRST = frozenset({"i", "me", "my", "mine", "myself", "i'm", "i've", "i'd", "i'll"})
_SECOND = frozenset({"you", "your", "yours", "yourself", "you're", "you've", "you'd", "you'll"})


def _mean(xs: Sequence[float]) -> float:
    return float(sum(xs) / len(xs)) if xs else 0.0


def unit_features(turns: Sequence[tuple], user_role: str = "user") -> list:
    """Query-blind features of ONE unit (a session or a turn) = ``turns`` [(role, text), ...].  Returns floats in ``FEATURE_NAMES`` order.

    Rates are per 1,000 characters unless stated.  ``user_role`` names the role counted as 'user' in the two role-split length features."""
    texts = [t for _, t in turns]
    full = "\n".join(texts)
    nch = max(1, len(full))
    k = 1000.0 / nch
    lowered = sanitize_text(full).lower()                  # lexical group: typography-invariant by construction
    words = _WORD.findall(lowered)
    nw = max(1, len(words))
    letters = [c for c in full if c.isalpha()]
    user_chars = [len(t) for r, t in turns if r == user_role]
    other_chars = [len(t) for r, t in turns if r != user_role]
    tot_user, tot_all = sum(user_chars), max(1, sum(len(t) for t in texts))
    f = {
        # typography
        "curly_apos": full.count("’") * k,
        "curly_quote": (full.count("“") + full.count("”")) * k,
        "dash_typo": (full.count("—") + full.count("–")) * k,
        "ellipsis": (full.count("…") + full.count("...")) * k,
        "nonascii": sum(1 for c in full if ord(c) > 127) * k,
        "emoji": len(_EMOJI.findall(full)) * k,
        "straight_apos": full.count("'") * k,
        # format
        "md_bold": len(_MD_BOLD.findall(full)) * k,
        "md_header": len(_MD_HEADER.findall(full)) * k,
        "md_bullet": len(_MD_BULLET.findall(full)) * k,
        "code_fence": full.count("```") * k,
        "newline": full.count("\n") * k,
        "url": len(_URL.findall(full)) * k,
        "paren": full.count("(") * k,
        "colon": full.count(":") * k,
        "question": full.count("?") * k,
        "exclaim": full.count("!") * k,
        # length
        "log_chars": math.log1p(len(full)),
        "n_turns": float(len(turns)),
        "user_mean_chars": _mean(user_chars),
        "other_mean_chars": _mean(other_chars),
        "max_turn_chars": float(max((len(t) for t in texts), default=0)),
        "user_char_share": tot_user / tot_all,
        # lexical-style (typography-invariant)
        "mean_word_len": _mean([len(w) for w in words]),
        "ttr": len(set(words[:400])) / max(1, min(len(words), 400)),
        "digit_rate": sum(1 for c in lowered if c.isdigit()) * 1000.0 / max(1, len(lowered)),
        "upper_rate": (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0.0,
        "first_person": sum(1 for w in words if w in _FIRST) / nw,
        "second_person": sum(1 for w in words if w in _SECOND) / nw,
        "contraction": sum(1 for w in words if "'" in w.strip("'")) / nw,
        "mean_sent_len": nw / max(1, len(_SENT.findall(lowered))),
    }
    return [float(f[n]) for n in FEATURE_NAMES]


def position_features(rel_pos: float, n_units: int) -> list:
    return [float(rel_pos), math.log1p(n_units)]
