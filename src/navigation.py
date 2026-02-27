"""
grandMA2 Console Navigation Module

High-level async API for navigating the MA2 console's object tree via telnet.
Combines three layers:

1. Command builder (src/commands/functions/navigation.py) — generates cd strings
2. Telnet client (src/telnet_client.py) — sends commands, captures raw response
3. Prompt parser (src/prompt_parser.py) — extracts prompt state from raw output

This module is the I/O boundary for navigation operations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Union

from src.commands import changedest
from src.prompt_parser import ConsolePrompt, parse_prompt
from src.telnet_client import GMA2TelnetClient


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NavigationResult:
    """Result of a navigation operation.

    Attributes:
        command_sent: The MA command string that was sent (e.g. ``"cd Group 1"``).
        raw_response: The complete raw telnet response.
        parsed_prompt: Parsed prompt state from the response.
        success: ``True`` if a prompt was detected, ``None`` if indeterminate.
    """

    command_sent: str
    raw_response: str
    parsed_prompt: ConsolePrompt
    success: Optional[bool] = None


async def navigate(
    client: GMA2TelnetClient,
    destination: str,
    object_id: Optional[Union[int, str]] = None,
    *,
    timeout: float = 2.0,
    delay: float = 0.3,
) -> NavigationResult:
    """Send a cd command and parse the resulting prompt.

    Args:
        client: Connected GMA2TelnetClient instance.
        destination: Navigation target (see :func:`changedest` for formats).
        object_id: Object ID when destination is an object type.
        timeout: Maximum time to wait for telnet response.
        delay: Initial delay after sending command.

    Returns:
        NavigationResult with command sent, raw response, and parsed prompt.
    """
    cmd = changedest(destination, object_id)
    logger.info("Navigating: %s", cmd)

    raw_response = await client.send_command_with_response(
        cmd, timeout=timeout, delay=delay
    )
    logger.debug(
        "Navigation raw response (%d chars): %r", len(raw_response), raw_response
    )

    parsed = parse_prompt(raw_response)

    success: Optional[bool] = None
    if parsed.prompt_line is not None:
        success = True

    result = NavigationResult(
        command_sent=cmd,
        raw_response=raw_response,
        parsed_prompt=parsed,
        success=success,
    )
    logger.info(
        "Navigation result: success=%s, location=%s", result.success, parsed.location
    )
    return result


async def get_current_location(
    client: GMA2TelnetClient,
    *,
    timeout: float = 2.0,
    delay: float = 0.3,
) -> NavigationResult:
    """Query the current console location without navigating.

    Sends an empty line to prompt the console to re-display its prompt.

    Args:
        client: Connected GMA2TelnetClient instance.
        timeout: Maximum time to wait for telnet response.
        delay: Initial delay after sending command.

    Returns:
        NavigationResult with the current parsed prompt state.
    """
    cmd = ""
    logger.info("Querying current console location (empty command)")

    raw_response = await client.send_command_with_response(
        cmd, timeout=timeout, delay=delay
    )
    logger.debug(
        "Location query raw response (%d chars): %r", len(raw_response), raw_response
    )

    parsed = parse_prompt(raw_response)

    success: Optional[bool] = True if parsed.prompt_line is not None else None

    return NavigationResult(
        command_sent=cmd,
        raw_response=raw_response,
        parsed_prompt=parsed,
        success=success,
    )
