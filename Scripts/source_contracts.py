"""Reusable static-source contract helpers.

These helpers intentionally validate structural semantics (for example, event publication
before mutation) without depending on the exact right-hand-side spelling of an assignment.
"""
from __future__ import annotations

import re
from typing import Iterable


def _blank(match: re.Match[str]) -> str:
    return " " * len(match.group(0))


def strip_comments_and_strings_preserve_length(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", _blank, text, flags=re.S)
    text = re.sub(r"//[^\n]*", _blank, text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', _blank, text)
    return text


def first_member_assignment_position(source: str, member_names: Iterable[str]) -> int:
    """Return the first assignment to one of the named members, ignoring comments/strings."""
    cleaned = strip_comments_and_strings_preserve_length(source)
    names = [re.escape(name) for name in member_names]
    if not names:
        return -1
    match = re.search(r"\b(?:" + "|".join(names) + r")\s*=", cleaned)
    return -1 if match is None else match.start()


def signal_precedes_member_mutation(
    source: str,
    signal_expression: str,
    member_names: Iterable[str],
) -> bool:
    """True only when the signal exists and appears before the first protected mutation."""
    cleaned = strip_comments_and_strings_preserve_length(source)
    signal_position = cleaned.find(signal_expression)
    mutation_position = first_member_assignment_position(source, member_names)
    return signal_position >= 0 and mutation_position >= 0 and signal_position < mutation_position
