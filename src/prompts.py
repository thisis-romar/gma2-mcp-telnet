"""
MCP Prompts Module

Pre-built prompt templates that encode grandMA2 domain expertise as
reusable workflows. These appear as slash-commands or selectable prompts
in MCP host applications.

Static prompts return fixed templates. Dynamic prompts (like show_status_report)
fetch live console state before generating the prompt.
"""

from __future__ import annotations

import json
import logging

from mcp.server.fastmcp import FastMCP

from src.tools import get_client, parse_listvar

logger = logging.getLogger(__name__)


def register_prompts(mcp: FastMCP) -> None:
    """Register all GMA2 prompt templates on the given FastMCP server."""

    @mcp.prompt(
        name="program-color-chase",
        description="Guided workflow for programming a color chase effect "
        "on a fixture group using sequences and cues.",
    )
    async def program_color_chase(
        fixture_group: str = "1",
        color_count: str = "4",
    ) -> list[dict]:
        """Step-by-step color chase programming guide."""
        return [
            {
                "role": "user",
                "content": (
                    f"Help me program a color chase with {color_count} colors "
                    f"on fixture group {fixture_group}.\n\n"
                    "Follow these steps using the available MCP tools:\n\n"
                    "1. **Select fixtures**: Use `set_intensity` or `apply_preset` to "
                    f"select group {fixture_group}\n"
                    "2. **Create a new sequence**: Use `store_cue` to create cues — "
                    f"one per color ({color_count} total)\n"
                    "3. **For each cue**:\n"
                    "   - Apply a color preset with `apply_preset(preset_type='color', ...)`\n"
                    "   - Store the cue with `store_cue(sequence_id=..., cue_id=N)`\n"
                    "   - Clear the programmer with `clear_programmer()`\n"
                    "4. **Set chase timing**: Each cue should have a fade time for smooth transitions\n"
                    "5. **Assign to executor**: Use `assign_object` to put the sequence on a fader\n\n"
                    "**Important MA2 tips:**\n"
                    "- Always `clear_programmer()` between cues to avoid data bleed\n"
                    "- Use `list_sequence_cues` to verify your work\n"
                    "- Color presets are PresetType 4 in MA2\n"
                    "- Store with `/merge` to avoid overwriting existing data"
                ),
            }
        ]

    @mcp.prompt(
        name="setup-moving-lights",
        description="Guided workflow for patching moving lights, "
        "creating groups, and storing focus presets.",
    )
    async def setup_moving_lights(
        fixture_type: str = "Mac 700",
        start_address: str = "1",
        count: str = "8",
    ) -> list[dict]:
        """Step-by-step moving light setup guide."""
        return [
            {
                "role": "user",
                "content": (
                    f"Help me set up {count} {fixture_type} moving lights "
                    f"starting at DMX address {start_address}.\n\n"
                    "Follow these steps using the available MCP tools:\n\n"
                    "1. **Check existing fixtures**: Use `list_console_destination` "
                    "after `navigate_console(destination='Fixture')` to see what's patched\n"
                    "2. **Verify DMX availability**: Check for address conflicts\n"
                    "3. **Create a fixture group**: Use `create_fixture_group` to group them "
                    "(confirm_destructive=True required)\n"
                    "4. **Store position presets**: Focus each position and use `store_preset` "
                    "with preset_type='position'\n"
                    "5. **Label everything**: Use `label_object` for clear naming\n\n"
                    "**Important MA2 tips:**\n"
                    "- DMX addresses auto-increment based on fixture channel count\n"
                    "- Groups are stored in the Group pool (cd 22)\n"
                    "- Position presets are PresetType 2\n"
                    "- Always label groups and presets for easy recall later\n"
                    "- Use `discover_object_names('Group')` to check existing groups"
                ),
            }
        ]

    @mcp.prompt(
        name="troubleshoot-connectivity",
        description="Diagnostic steps to troubleshoot Telnet connectivity "
        "issues between the MCP server and grandMA2 onPC.",
    )
    async def troubleshoot_connectivity() -> list[dict]:
        """Telnet connectivity troubleshooting guide."""
        return [
            {
                "role": "user",
                "content": (
                    "Help me troubleshoot the connection between this MCP server "
                    "and the grandMA2 onPC console.\n\n"
                    "Run these diagnostic steps:\n\n"
                    "1. **Check system variables**: Use `list_system_variables()` — "
                    "if this works, the connection is alive\n"
                    "2. **Verify console status**: Check `$HOSTSTATUS` — should show "
                    "'Master' or 'Standalone'\n"
                    "3. **Check login**: `$USER` should show the logged-in user\n"
                    "4. **Test navigation**: `get_console_location()` should return "
                    "a valid prompt\n"
                    "5. **Test a safe command**: `list_console_destination()` at root "
                    "should list the object tree\n\n"
                    "**Common issues:**\n"
                    "- 'Connection refused' → grandMA2 onPC not running or Telnet not enabled\n"
                    "  Fix: Setup → Console → Global Settings → Telnet = Login Enabled\n"
                    "- 'Login failed' → wrong credentials (check GMA_USER / GMA_PASSWORD env vars)\n"
                    "  Default: administrator / admin\n"
                    "- 'Connection lost' → show was reset without /globalsettings\n"
                    "  Fix: use new_show with preserve_connectivity=True (the default)\n"
                    "- Slow responses → network latency or console under heavy load\n"
                    "  Check: GMA_HOST should be 127.0.0.1 for local onPC"
                ),
            }
        ]

    @mcp.prompt(
        name="create-cue-sequence",
        description="Step-by-step guide to create a cue sequence "
        "with proper programmer management.",
    )
    async def create_cue_sequence(
        sequence_id: str = "1",
        cue_count: str = "5",
    ) -> list[dict]:
        """Cue sequence creation guide."""
        return [
            {
                "role": "user",
                "content": (
                    f"Help me create a sequence (ID {sequence_id}) with "
                    f"{cue_count} cues.\n\n"
                    "Follow these steps using the available MCP tools:\n\n"
                    "1. **Clear programmer first**: `clear_programmer()` to start fresh\n"
                    "2. **For each cue (1 through " + cue_count + ")**:\n"
                    "   a. Select fixtures and set their values\n"
                    "   b. Store: `store_cue(sequence_id=" + sequence_id + ", cue_id=N, "
                    "confirm_destructive=True)`\n"
                    "   c. Clear: `clear_programmer()` before the next cue\n"
                    "3. **Verify**: `list_sequence_cues(sequence_id=" + sequence_id + ")` "
                    "to see all stored cues\n"
                    "4. **Assign to executor**: `assign_object(object_type='sequence', "
                    "object_id=" + sequence_id + ", executor_id=1, confirm_destructive=True)`\n"
                    "5. **Test playback**: `playback_action(action='go', "
                    "executor_id=1)` to run through cues\n\n"
                    "**Important MA2 tips:**\n"
                    "- ALWAYS clear programmer between cues — uncleared values carry over\n"
                    "- Use `/merge` flag when updating existing cues to avoid data loss\n"
                    "- Cue IDs can be decimals (e.g. 1.5) for point cues\n"
                    "- Store operations are DESTRUCTIVE — confirm_destructive=True is required\n"
                    "- Use `update_cue` to modify timing after storing"
                ),
            }
        ]

    @mcp.prompt(
        name="show-status-report",
        description="Dynamic prompt that fetches live console state "
        "and presents a comprehensive status report.",
    )
    async def show_status_report() -> list[dict]:
        """Fetch live console state and build a status summary prompt."""
        try:
            client = await get_client()
            raw = await client.send_command_with_response("ListVar")
            variables = parse_listvar(raw)
        except Exception as exc:
            logger.warning("Could not fetch console state: %s", exc)
            variables = {}

        if variables:
            var_lines = "\n".join(f"  {k} = {v}" for k, v in sorted(variables.items()))
            status_block = (
                "**Live Console State:**\n"
                f"```\n{var_lines}\n```\n\n"
                f"Show: {variables.get('$SHOWFILE', 'unknown')}\n"
                f"Version: {variables.get('$VERSION', 'unknown')}\n"
                f"User: {variables.get('$USER', 'unknown')} "
                f"({variables.get('$USERRIGHTS', 'unknown')})\n"
                f"Host: {variables.get('$HOSTNAME', 'unknown')} "
                f"({variables.get('$HOSTIP', 'unknown')})\n"
                f"Status: {variables.get('$HOSTSTATUS', 'unknown')}\n"
                f"Selected Executor: {variables.get('$SELECTEDEXEC', 'none')}\n"
                f"Fader Page: {variables.get('$FADERPAGE', 'unknown')}\n"
            )
        else:
            status_block = (
                "**Console state unavailable** — could not connect to grandMA2.\n"
                "Use the `troubleshoot-connectivity` prompt for diagnostics.\n"
            )

        return [
            {
                "role": "user",
                "content": (
                    "Give me a status report on the current grandMA2 console state "
                    "and suggest what I should work on next.\n\n"
                    f"{status_block}\n"
                    "Based on this state:\n"
                    "1. Summarize the console's current configuration\n"
                    "2. Note any potential issues (e.g. default credentials, no fixtures)\n"
                    "3. Suggest next steps based on the show state"
                ),
            }
        ]
