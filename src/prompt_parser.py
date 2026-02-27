"""
grandMA2 Telnet Prompt Parser

Parses raw telnet output to detect the grandMA2 command-line prompt and
extract the current navigation destination (object tree location).

The exact prompt format is discovered empirically by sending commands and
inspecting responses.  This module uses a flexible multi-pattern approach
so it can be refined as we learn the real format from live consoles.

Candidate prompt patterns (ordered by specificity):
  1. ``[something]>``  or ``[something]>/`` — bracket-delimited
  2. Lines ending with ``>`` after stripping whitespace
  3. Fallback: no prompt detected
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ConsolePrompt:
    """Parsed console prompt state extracted from raw telnet output.

    Attributes:
        raw_response: The complete raw telnet output.
        prompt_line: The detected prompt line (e.g. ``[Group 1]>``), or
            ``None`` if no prompt pattern was matched.
        location: Extracted location text from inside the prompt brackets
            (e.g. ``"Group 1"``), or ``None``.
        object_type: Parsed object type if the location contains a
            recognizable ``Type ID`` pattern (e.g. ``"Group"``), or ``None``.
        object_id: Parsed object ID from the location (e.g. ``"1"``),
            or ``None``.
    """

    raw_response: str
    prompt_line: Optional[str] = None
    location: Optional[str] = None
    object_type: Optional[str] = None
    object_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Prompt detection patterns (tried in order)
# ---------------------------------------------------------------------------

# Pattern 1: bracket-delimited prompt  [content]>  or  [content]>/
_BRACKET_PROMPT_RE = re.compile(r"\[(.+?)\]\s*>/?\s*$", re.MULTILINE)

# Pattern 2: line ending with >
_ANGLE_PROMPT_RE = re.compile(r"^(.+)>\s*$", re.MULTILINE)

# ---------------------------------------------------------------------------
# Location splitting: "Group 1" -> object_type="Group", object_id="1"
# ---------------------------------------------------------------------------

_LOCATION_SPLIT_RE = re.compile(r"^([A-Za-z]+)\s+(\d+(?:\.\d+)?)$")
_LOCATION_SINGLE_RE = re.compile(r"^[A-Za-z]\w*$")


def _split_location(location: str) -> tuple[Optional[str], Optional[str]]:
    """Attempt to split a location string into object_type and object_id.

    Returns ``(object_type, object_id)`` for ``"Group 1"`` style strings,
    ``(object_type, None)`` for single-word locations like ``"Fixture"``,
    or ``(None, None)`` if the location doesn't match any expected pattern.
    """
    if not location:
        return None, None

    # "Group 1", "Preset 4.1"
    m = _LOCATION_SPLIT_RE.match(location)
    if m:
        return m.group(1), m.group(2)

    # "Fixture", "Root", "channel"
    if _LOCATION_SINGLE_RE.match(location):
        return location, None

    return None, None


def parse_prompt(raw: str) -> ConsolePrompt:
    """Parse raw telnet output and attempt to detect the MA2 prompt.

    Tries multiple candidate patterns against the raw output.  Returns a
    :class:`ConsolePrompt` with as much information as could be extracted.
    If no prompt pattern matches, ``prompt_line`` and derived fields will
    be ``None`` — the ``raw_response`` is always preserved so callers can
    inspect the output manually.

    Args:
        raw: Raw telnet output string.

    Returns:
        Parsed :class:`ConsolePrompt`.
    """
    if not raw:
        return ConsolePrompt(raw_response=raw)

    # Try pattern 1: bracket-delimited [content]>
    matches = list(_BRACKET_PROMPT_RE.finditer(raw))
    if matches:
        # Use the last match (prompt is typically at the end of output)
        last = matches[-1]
        prompt_line = last.group(0).strip()
        location = last.group(1).strip()
        obj_type, obj_id = _split_location(location)
        return ConsolePrompt(
            raw_response=raw,
            prompt_line=prompt_line,
            location=location,
            object_type=obj_type,
            object_id=obj_id,
        )

    # Try pattern 2: line ending with >
    matches = list(_ANGLE_PROMPT_RE.finditer(raw))
    if matches:
        last = matches[-1]
        prompt_line = last.group(0).strip()
        content = last.group(1).strip()
        # The content before > might contain location info
        obj_type, obj_id = _split_location(content)
        return ConsolePrompt(
            raw_response=raw,
            prompt_line=prompt_line,
            location=content if content else None,
            object_type=obj_type,
            object_id=obj_id,
        )

    # No prompt detected — return raw only
    return ConsolePrompt(raw_response=raw)
