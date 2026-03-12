"""
MCP Resources Module

Exposes grandMA2 console state as read-only MCP resources.
Resources provide structured data that AI clients can query without
executing commands — complementing the action-oriented tools.

All resources are SAFE_READ: no safety gate required.
"""

from __future__ import annotations

import json
import logging

from mcp.server.fastmcp import FastMCP

from src.navigation import get_current_location, list_destination, navigate
from src.tools import get_client, parse_listvar

logger = logging.getLogger(__name__)


def register_resources(mcp: FastMCP) -> None:
    """Register all GMA2 resources on the given FastMCP server."""

    @mcp.resource(
        "gma2://console/status",
        name="console_status",
        description="All 26 grandMA2 system variables (read-only). "
        "Includes $TIME, $DATE, $SHOWFILE, $VERSION, $HOSTNAME, "
        "$SELECTEDEXEC, $FADERPAGE, $USER, etc.",
        mime_type="application/json",
    )
    async def console_status() -> str:
        """Return all system variables as JSON."""
        client = await get_client()
        raw = await client.send_command_with_response("ListVar")
        variables = parse_listvar(raw)
        return json.dumps(variables, indent=2)

    @mcp.resource(
        "gma2://console/location",
        name="console_location",
        description="Current console cd location and prompt text. "
        "Shows where the console is navigated to in the object tree.",
        mime_type="application/json",
    )
    async def console_location() -> str:
        """Return the current console navigation location."""
        client = await get_client()
        nav = await get_current_location(client)
        parsed = nav.parsed_prompt
        return json.dumps(
            {
                "location": parsed.location,
                "prompt_line": parsed.prompt_line,
                "raw_response": nav.raw_response,
            },
            indent=2,
        )

    @mcp.resource(
        "gma2://show/fixtures",
        name="show_fixtures",
        description="Fixture pool listing from the current show. "
        "Returns all fixture entries with IDs and names.",
        mime_type="application/json",
    )
    async def show_fixtures() -> str:
        """Navigate to the fixture pool, list all entries, return to root."""
        return await _list_pool("Fixture")

    @mcp.resource(
        "gma2://show/groups",
        name="show_groups",
        description="Group pool listing from the current show. "
        "Returns all group entries with IDs and names.",
        mime_type="application/json",
    )
    async def show_groups() -> str:
        """Navigate to the group pool, list all entries, return to root."""
        return await _list_pool("Group")

    @mcp.resource(
        "gma2://show/sequences",
        name="show_sequences",
        description="Sequence pool listing from the current show. "
        "Returns all sequence entries with IDs and names.",
        mime_type="application/json",
    )
    async def show_sequences() -> str:
        """Navigate to the sequence pool, list all entries, return to root."""
        return await _list_pool("Sequence")

    @mcp.resource(
        "gma2://show/sequences/{seq_id}/cues",
        name="sequence_cues",
        description="List cues in a specific sequence. "
        "Pass the sequence number as {seq_id} in the URI.",
        mime_type="application/json",
    )
    async def sequence_cues(seq_id: str) -> str:
        """Navigate to a specific sequence and list its cues."""
        client = await get_client()
        try:
            nav = await navigate(client, "Sequence", object_id=seq_id)
            lst = await list_destination(client)
            entries = [
                {
                    "object_type": e.object_type,
                    "object_id": e.object_id,
                    "name": e.name,
                    **({"columns": e.columns} if e.columns else {}),
                }
                for e in lst.parsed_list.entries
            ]
            return json.dumps(
                {
                    "sequence_id": seq_id,
                    "navigate_command": nav.command_sent,
                    "cue_count": len(entries),
                    "cues": entries,
                },
                indent=2,
            )
        finally:
            await navigate(client, "/")


async def _list_pool(destination: str) -> str:
    """Shared helper: cd to a pool, list entries, cd / back to root."""
    client = await get_client()
    try:
        nav = await navigate(client, destination)
        lst = await list_destination(client)
        entries = [
            {
                "object_type": e.object_type,
                "object_id": e.object_id,
                "name": e.name,
                **({"columns": e.columns} if e.columns else {}),
            }
            for e in lst.parsed_list.entries
        ]
        return json.dumps(
            {
                "pool": destination,
                "navigate_command": nav.command_sent,
                "entry_count": len(entries),
                "entries": entries,
            },
            indent=2,
        )
    finally:
        await navigate(client, "/")
