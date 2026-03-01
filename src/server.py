"""
MCP Server Module

This module is responsible for creating and running the MCP server,
integrating all tools together. It uses FastMCP to simplify the MCP server setup.

Usage:
    uv run python -m src.server
"""

import json
import logging
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.telnet_client import GMA2TelnetClient
from src.tools import set_gma2_client
from src.commands import (
    select_fixture,
    store_group,
    label_group,
    go_sequence,
    pause_sequence,
    goto_cue,
)
from src.navigation import navigate, get_current_location, list_destination, scan_indexes, set_property
from src.vocab import RiskTier, build_v39_spec, classify_token

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
GMA_HOST = os.getenv("GMA_HOST", "127.0.0.1")
GMA_PORT = int(os.getenv("GMA_PORT", "30000"))
GMA_USER = os.getenv("GMA_USER", "administrator")
GMA_PASSWORD = os.getenv("GMA_PASSWORD", "admin")
GMA_SAFETY_LEVEL = os.getenv("GMA_SAFETY_LEVEL", "standard").lower()

# Build vocab spec once for token classification / safety gating
_vocab_spec = build_v39_spec()

# Create MCP server
mcp = FastMCP(
    name="grandMA2-MCP",
    instructions="""
    This is an MCP server for controlling grandMA2 lighting console.
    You can use the following tools to operate grandMA2:

    1. create_fixture_group - Create a fixture group
       Example: Save fixtures 1 to 10 as group 1 with name "Front Wash"

    2. execute_sequence - Execute sequence operations
       Example: Execute sequence 1, pause sequence 2, jump to cue 5 of sequence 1

    3. send_raw_command - Send raw MA commands
       Example: Send "blackout" or "go+ executor 1.1"

    4. navigate_console - Navigate the console's object tree (ChangeDest/cd)
       Example: cd to "Group.1", go up with "..", return to root with "/"
       Returns raw telnet response + parsed prompt state for exploration.

    5. get_console_location - Query the current console destination
       Returns raw telnet response + parsed prompt state without navigating.

    6. list_console_destination - List objects at the current destination
       After cd-ing into a location, run list to enumerate children.
       Returns parsed entries with object-type, object-id, and element names.

    7. set_node_property - Set a property on a node in the object tree
       Uses dot-separated index paths from the scan tree output.
       Example: path="3.1", property_name="Telnet", value="Login Disabled"
    """,
)

# Global telnet client instance
_client: GMA2TelnetClient | None = None
_connected: bool = False


async def get_client() -> GMA2TelnetClient:
    """
    Get or create a telnet client instance (async).

    On first call, establishes connection and login. Subsequent calls return
    the already connected client. If the connection has dropped, reconnects
    automatically.
    """
    global _client, _connected

    # Check if existing connection is still healthy
    if _client is not None and _connected:
        if _client._writer is None:
            logger.warning("Connection lost, reconnecting...")
            _connected = False

    if _client is None or not _connected:
        _client = GMA2TelnetClient(
            host=GMA_HOST,
            port=GMA_PORT,
            user=GMA_USER,
            password=GMA_PASSWORD,
        )
        try:
            await _client.connect()
            await _client.login()
            _connected = True
            set_gma2_client(_client)
            logger.info(f"Connected to grandMA2: {GMA_HOST}:{GMA_PORT}")
        except Exception:
            _connected = False
            raise

    return _client


# ============================================================
# MCP Tools Definition
# ============================================================


@mcp.tool()
async def create_fixture_group(
    start_fixture: int,
    end_fixture: int,
    group_id: int,
    group_name: str | None = None,
) -> str:
    """
    Create a group containing a specified range of fixtures.

    This tool selects the specified range of fixtures and saves them as a group.
    Optionally, a name can be assigned to the group.

    Args:
        start_fixture: Starting fixture number
        end_fixture: Ending fixture number
        group_id: Group number to save
        group_name: (Optional) Group name, e.g., "Front Wash"

    Returns:
        str: Operation result message

    Examples:
        - Save fixtures 1 to 10 as group 1
        - Save fixtures 1 to 10 as group 1 with name "Front Wash"
    """
    client = await get_client()

    # Select fixtures
    select_cmd = select_fixture(start_fixture, end_fixture)
    await client.send_command(select_cmd)

    # Save as group
    store_cmd = store_group(group_id)
    await client.send_command(store_cmd)

    # Add label if name is provided
    if group_name:
        label_cmd = label_group(group_id, group_name)
        await client.send_command(label_cmd)
        return f'Created Group {group_id} "{group_name}" containing Fixtures {start_fixture} to {end_fixture}'

    return (
        f"Created Group {group_id} containing Fixtures {start_fixture} to {end_fixture}"
    )


@mcp.tool()
async def execute_sequence(
    sequence_id: int,
    action: str,
    cue_id: int | None = None,
) -> str:
    """
    Execute sequence-related operations.

    Args:
        sequence_id: Sequence number
        action: Operation type: "go" (execute), "pause" (pause), or "goto" (jump to cue)
        cue_id: (Required for goto) Target cue number

    Returns:
        str: Operation result message

    Examples:
        - Execute sequence 1
        - Pause sequence 2
        - Jump to cue 5 of sequence 1
    """
    client = await get_client()

    if action == "go":
        cmd = go_sequence(sequence_id)
        await client.send_command(cmd)
        return f"Executed Sequence {sequence_id}"

    elif action == "pause":
        cmd = pause_sequence(sequence_id)
        await client.send_command(cmd)
        return f"Paused Sequence {sequence_id}"

    elif action == "goto":
        if cue_id is None:
            return "Error: goto action requires cue_id to be specified"
        cmd = goto_cue(sequence_id, cue_id)
        await client.send_command(cmd)
        return f"Jumped to Cue {cue_id} of Sequence {sequence_id}"

    return f"Unknown action: {action}, use go, pause, or goto"


@mcp.tool()
async def send_raw_command(
    command: str,
    confirm_destructive: bool = False,
) -> str:
    """
    Send a raw MA command to grandMA2 and return the console response.

    WARNING: This is a low-level tool that sends commands directly to a LIVE
    lighting console. Prefer the higher-level tools (create_fixture_group,
    execute_sequence) whenever possible.

    SAFETY: Commands are classified by risk tier before sending:
    - SAFE_READ (list, info, cd): Always allowed
    - SAFE_WRITE (at, go, clear, blackout): Allowed in standard and admin mode
    - DESTRUCTIVE (delete, store, assign, shutdown): Blocked unless
      confirm_destructive=True. Set GMA_SAFETY_LEVEL=admin to skip checks.

    Args:
        command: Raw MA command to send
        confirm_destructive: Must be True to send destructive commands
            (delete, store, assign, shutdown, newshow, etc.)

    Returns:
        str: JSON with command_sent, risk_tier, raw_response, and any
            safety block information.

    Examples:
        - go+ executor 1.1
        - list cue
        - store sequence 1 cue 1 (requires confirm_destructive=True)
    """
    # Input sanitization: reject line breaks that could inject commands
    if "\r" in command or "\n" in command:
        return json.dumps({
            "command_sent": None,
            "error": "Command contains line breaks (\\r or \\n) which could "
                     "inject additional commands. Remove them and retry.",
            "blocked": True,
        }, indent=2)

    # Safety gate: classify the first token
    first_token = command.strip().split()[0] if command.strip() else ""
    resolved = classify_token(first_token, _vocab_spec)
    risk = resolved.risk

    # Block destructive commands unless explicitly confirmed or admin mode
    if risk == RiskTier.DESTRUCTIVE and GMA_SAFETY_LEVEL != "admin":
        if not confirm_destructive:
            logger.warning(
                "BLOCKED destructive command: %r (risk=%s, canonical=%s)",
                command, risk.value, resolved.canonical,
            )
            return json.dumps({
                "command_sent": None,
                "risk_tier": risk.value,
                "canonical_keyword": resolved.canonical,
                "error": (
                    f"Command '{first_token}' is classified as {risk.value}. "
                    f"Set confirm_destructive=True to proceed, or use "
                    f"GMA_SAFETY_LEVEL=admin to disable safety checks."
                ),
                "blocked": True,
            }, indent=2)
        logger.warning(
            "CONFIRMED destructive command: %r (risk=%s, canonical=%s)",
            command, risk.value, resolved.canonical,
        )

    # Block all write commands in read-only mode
    if GMA_SAFETY_LEVEL == "read-only" and risk != RiskTier.SAFE_READ:
        logger.warning(
            "BLOCKED non-read command in read-only mode: %r (risk=%s)",
            command, risk.value,
        )
        return json.dumps({
            "command_sent": None,
            "risk_tier": risk.value,
            "error": (
                f"Server is in read-only mode (GMA_SAFETY_LEVEL=read-only). "
                f"Only SAFE_READ commands (list, info, cd) are allowed."
            ),
            "blocked": True,
        }, indent=2)

    logger.info(
        "Sending command: %r (risk=%s, canonical=%s)",
        command, risk.value, resolved.canonical,
    )

    client = await get_client()
    raw_response = await client.send_command_with_response(command)

    return json.dumps({
        "command_sent": command,
        "risk_tier": risk.value,
        "canonical_keyword": resolved.canonical,
        "raw_response": raw_response,
        "blocked": False,
    }, indent=2)


@mcp.tool()
async def navigate_console(
    destination: str,
    object_id: int | None = None,
) -> str:
    """
    Navigate the grandMA2 console's object tree using ChangeDest (cd).

    Sends a cd command and captures the raw telnet response, attempting
    to parse the resulting console prompt to determine the current
    location in the object tree.

    EXPLORATORY: The exact MA2 telnet prompt format is being validated.
    The raw_response field always contains the unmodified telnet output
    for manual inspection, regardless of whether parsing succeeded.

    Args:
        destination: Navigation target. Supported formats:
            - "/" to go to root
            - ".." to go up one level
            - A number (e.g., "5") to navigate by index
            - An object type (e.g., "Group") when object_id is provided
              (uses dot notation: cd Group.1)
            - A quoted name (e.g., '"MySequence"') to navigate by name
        object_id: Object ID, produces dot notation cd [type].[id]
            (e.g., destination="Group", object_id=1 → cd Group.1)

    Returns:
        str: JSON with command_sent, raw_response, parsed prompt details,
             and success indicator.

    Examples:
        - Navigate to root: destination="/"
        - Go up one level: destination=".."
        - Navigate to Group 1: destination="Group", object_id=1 → cd Group.1
        - Navigate by index: destination="5"
        - After navigating, use list_console_destination to enumerate objects
    """
    client = await get_client()
    result = await navigate(client, destination, object_id)

    return json.dumps(
        {
            "command_sent": result.command_sent,
            "raw_response": result.raw_response,
            "success": result.success,
            "parsed_prompt": {
                "prompt_line": result.parsed_prompt.prompt_line,
                "location": result.parsed_prompt.location,
                "object_type": result.parsed_prompt.object_type,
                "object_id": result.parsed_prompt.object_id,
            },
        },
        indent=2,
    )


@mcp.tool()
async def get_console_location() -> str:
    """
    Query the current grandMA2 console destination without navigating.

    Sends an empty command to prompt the console to re-display its
    prompt, then parses the response to determine the current location.

    Returns:
        str: JSON with raw_response, parsed prompt details,
             and success indicator.
    """
    client = await get_client()
    result = await get_current_location(client)

    return json.dumps(
        {
            "command_sent": result.command_sent,
            "raw_response": result.raw_response,
            "success": result.success,
            "parsed_prompt": {
                "prompt_line": result.parsed_prompt.prompt_line,
                "location": result.parsed_prompt.location,
                "object_type": result.parsed_prompt.object_type,
                "object_id": result.parsed_prompt.object_id,
            },
        },
        indent=2,
    )


@mcp.tool()
async def list_console_destination(
    object_type: str | None = None,
) -> str:
    """
    List objects at the current grandMA2 console destination.

    After navigating with cd (navigate_console), use this tool to
    enumerate children at the current location.  Parses the list
    feedback to extract object-type, object-id, and element names.

    Args:
        object_type: Optional filter (e.g., "cue", "group", "preset").
            If omitted, lists everything at the current destination.

    Returns:
        str: JSON with command_sent, raw_response, and parsed entries
             (each with object_type, object_id, name).
    """
    client = await get_client()
    result = await list_destination(client, object_type)

    entries_out = []
    for e in result.parsed_list.entries:
        entry = {
            "object_type": e.object_type,
            "object_id": e.object_id,
            "name": e.name,
            "raw_line": e.raw_line,
        }
        if e.col3 is not None:
            entry["col3"] = e.col3
        if e.columns:
            entry["columns"] = e.columns
        entries_out.append(entry)

    return json.dumps(
        {
            "command_sent": result.command_sent,
            "raw_response": result.raw_response,
            "entries": entries_out,
            "entry_count": len(result.parsed_list.entries),
        },
        indent=2,
    )


@mcp.tool()
async def scan_console_indexes(
    reset_to: str = "/",
    max_index: int = 50,
    stop_after_failures: int = 3,
) -> str:
    """
    Scan numeric indexes via cd N → list → cd <reset_to>.

    For each index N from 1 to max_index:
      1. cd N           — navigate into that index
      2. list           — enumerate children there
      3. cd <reset_to>  — return to the base location for the next iteration

    The reset_to destination controls what each cd N is relative to:
      - "/"          (default) scan root-level indexes (Showfile, TimeConfig, …)
      - "Sequence"   reset to Sequence pool → cd N enters Sequence N → list shows its cues
      - "Group"      reset to Group pool → cd N enters Group N

    Stops early after stop_after_failures consecutive indexes with no entries.

    Args:
        reset_to: Where to navigate after each list before the next cd N (default "/").
        max_index: Highest index to try (default 50).
        stop_after_failures: Stop after this many consecutive empty indexes (default 3).

    Returns:
        str: JSON with a list of scan results — one entry per index that
             returned list output, each with index, location, object_type,
             and parsed entries (object_type, object_id, name).
    """
    client = await get_client()
    results = await scan_indexes(
        client,
        reset_to=reset_to,
        max_index=max_index,
        stop_after_failures=stop_after_failures,
    )

    return json.dumps(
        {
            "scanned_count": len(results),
            "results": [
                {
                    "index": r.index,
                    "location": r.location,
                    "object_type": r.object_type,
                    "entry_count": len(r.entries),
                    "entries": [
                        {
                            "object_type": e.object_type,
                            "object_id": e.object_id,
                            "name": e.name,
                        }
                        for e in r.entries
                    ],
                }
                for r in results
            ],
        },
        indent=2,
    )


@mcp.tool()
async def set_node_property(
    path: str,
    property_name: str,
    value: str,
    verify: bool = True,
) -> str:
    """
    Set a property on a node in the grandMA2 object tree.

    Uses the scan tree path notation (dot-separated indexes) to navigate
    to a node and set an inline property using Assign [index]/property=value.

    The path uses the same index-based notation as the scan tree output.
    Split the path into parent segments and target index:
    - "3.1" → cd 3 (Settings), then Assign 1/property=value (on Global)
    - "4.1" → cd 4 (DMX_Protocols), then Assign 1/property=value (on Art-Net)
    - "3" → at root, Assign 3/property=value (on Settings itself)

    After setting, navigates back to root (cd /).
    If verify=True (default), re-lists and confirms the property changed.

    SAFETY: This modifies live console state. Double-check property names
    and values before calling. Use list_console_destination to inspect
    current values first.

    Args:
        path: Dot-separated index path (e.g. "3.1" for Settings/Global)
        property_name: Property to set (e.g. "Telnet", "OutActive")
        value: New value (e.g. "Login Enabled", "On")
        verify: Re-list after setting to confirm the change (default True)

    Returns:
        str: JSON with commands_sent, success, verified_value, and any errors.

    Examples:
        - Set telnet to disabled: path="3.1", property_name="Telnet", value="Login Disabled"
        - Enable Art-Net output: path="4.1", property_name="OutActive", value="On"
    """
    client = await get_client()
    result = await set_property(
        client,
        path,
        property_name,
        value,
        verify=verify,
    )

    return json.dumps(
        {
            "path": result.path,
            "property_name": property_name,
            "value": value,
            "commands_sent": result.commands_sent,
            "success": result.success,
            "verified_value": result.verified_value,
            "error": result.error,
        },
        indent=2,
    )


# ============================================================
# Server Startup
# ============================================================


def main():
    """MCP Server entry point."""
    logger.info("Starting grandMA2 MCP Server...")
    logger.info(f"Connecting to grandMA2: {GMA_HOST}:{GMA_PORT}")

    # Start server using stdio transport
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
