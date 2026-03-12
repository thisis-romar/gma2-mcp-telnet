"""Tests for MCP Resources (src/resources.py).

All tests mock get_client() — no live console needed.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.prompt_parser import ConsolePrompt, ListEntry, ListOutput
from src.navigation import ListDestinationResult, NavigationResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_nav_result(location: str = "Fixture") -> NavigationResult:
    """Build a NavigationResult with a parsed prompt."""
    raw = f"[channel  ]{location}>"
    return NavigationResult(
        command_sent=f"cd {location}",
        raw_response=raw,
        parsed_prompt=ConsolePrompt(
            raw_response=raw,
            prompt_line=raw,
            location=location,
        ),
        success=True,
    )


def _mock_list_result(entries: list[ListEntry] | None = None) -> ListDestinationResult:
    """Build a ListDestinationResult."""
    if entries is None:
        entries = []
    return ListDestinationResult(
        command_sent="list",
        raw_response="",
        parsed_list=ListOutput(
            raw_response="",
            entries=tuple(entries),
        ),
    )


# ---------------------------------------------------------------------------
# console_status
# ---------------------------------------------------------------------------

class TestConsoleStatusResource:
    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    async def test_returns_system_variables(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.send_command_with_response = AsyncMock(return_value=(
            "[channel  ]Fixture>\n"
            "$Global : $SHOWFILE = my_show\n"
            "$Global : $VERSION = 3.9.60.65\n"
            "$Global : $TIME = 12h00m00.000s\n"
        ))
        mock_get_client.return_value = mock_client

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        # Call the resource function directly
        # We need to access the registered function
        result = await _call_resource(mcp, "gma2://console/status")
        data = json.loads(result)

        assert "$SHOWFILE" in data
        assert data["$SHOWFILE"] == "my_show"
        assert "$VERSION" in data
        assert data["$VERSION"] == "3.9.60.65"
        assert "$TIME" in data

    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    async def test_empty_listvar(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.send_command_with_response = AsyncMock(return_value="[channel  ]Fixture>")
        mock_get_client.return_value = mock_client

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource(mcp, "gma2://console/status")
        data = json.loads(result)
        assert data == {}


# ---------------------------------------------------------------------------
# console_location
# ---------------------------------------------------------------------------

class TestConsoleLocationResource:
    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.get_current_location")
    async def test_returns_location(self, mock_get_location, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_get_location.return_value = NavigationResult(
            command_sent="",
            raw_response="[channel  ]Group>",
            parsed_prompt=ConsolePrompt(
                raw_response="[channel  ]Group>",
                prompt_line="[channel  ]Group>",
                location="Group",
            ),
            success=True,
        )

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource(mcp, "gma2://console/location")
        data = json.loads(result)

        assert data["location"] == "Group"
        assert "prompt_line" in data
        assert "raw_response" in data


# ---------------------------------------------------------------------------
# show_fixtures
# ---------------------------------------------------------------------------

class TestShowFixturesResource:
    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_lists_fixtures(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Fixture")
        mock_list.return_value = _mock_list_result([
            ListEntry(object_type="FixtureType", object_id=1, name="Mac 700"),
            ListEntry(object_type="FixtureType", object_id=2, name="Generic Dimmer"),
        ])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource(mcp, "gma2://show/fixtures")
        data = json.loads(result)

        assert data["pool"] == "Fixture"
        assert data["entry_count"] == 2
        assert data["entries"][0]["name"] == "Mac 700"
        assert data["entries"][1]["name"] == "Generic Dimmer"

    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_returns_to_root(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Fixture")
        mock_list.return_value = _mock_list_result([])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        await _call_resource(mcp, "gma2://show/fixtures")

        # Should have navigated twice: once to Fixture, once back to root
        assert mock_nav.call_count == 2
        assert mock_nav.call_args_list[1][0][1] == "/"

    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_empty_pool(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Fixture")
        mock_list.return_value = _mock_list_result([])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource(mcp, "gma2://show/fixtures")
        data = json.loads(result)
        assert data["entry_count"] == 0
        assert data["entries"] == []


# ---------------------------------------------------------------------------
# show_groups
# ---------------------------------------------------------------------------

class TestShowGroupsResource:
    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_lists_groups(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Group")
        mock_list.return_value = _mock_list_result([
            ListEntry(object_type="Group", object_id=1, name="Front Wash"),
            ListEntry(object_type="Group", object_id=2, name="Back Wash"),
        ])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource(mcp, "gma2://show/groups")
        data = json.loads(result)
        assert data["pool"] == "Group"
        assert data["entry_count"] == 2


# ---------------------------------------------------------------------------
# show_sequences
# ---------------------------------------------------------------------------

class TestShowSequencesResource:
    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_lists_sequences(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Sequence")
        mock_list.return_value = _mock_list_result([
            ListEntry(object_type="Sequence", object_id=1, name="Main Show"),
        ])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource(mcp, "gma2://show/sequences")
        data = json.loads(result)
        assert data["pool"] == "Sequence"
        assert data["entry_count"] == 1
        assert data["entries"][0]["name"] == "Main Show"


# ---------------------------------------------------------------------------
# sequence_cues (resource template)
# ---------------------------------------------------------------------------

class TestSequenceCuesResource:
    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_lists_cues_for_sequence(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Sequence")
        mock_list.return_value = _mock_list_result([
            ListEntry(object_type="Cue", object_id=1, name="Opening"),
            ListEntry(object_type="Cue", object_id=2, name="Verse 1"),
            ListEntry(object_type="Cue", object_id=3, name="Chorus"),
        ])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource_template(
            mcp, "gma2://show/sequences/{seq_id}/cues", seq_id="5"
        )
        data = json.loads(result)

        assert data["sequence_id"] == "5"
        assert data["cue_count"] == 3
        assert data["cues"][0]["name"] == "Opening"
        assert data["cues"][2]["name"] == "Chorus"

    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_navigates_to_sequence_and_back(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Sequence")
        mock_list.return_value = _mock_list_result([])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        await _call_resource_template(
            mcp, "gma2://show/sequences/{seq_id}/cues", seq_id="10"
        )

        # Navigate to Sequence.10, then back to /
        assert mock_nav.call_count == 2
        first_call = mock_nav.call_args_list[0]
        assert first_call[0][1] == "Sequence"
        assert first_call[1].get("object_id") or first_call[0][2] == "10"
        last_call = mock_nav.call_args_list[1]
        assert last_call[0][1] == "/"

    @pytest.mark.asyncio
    @patch("src.resources.get_client")
    @patch("src.resources.navigate")
    @patch("src.resources.list_destination")
    async def test_extras_included_when_present(self, mock_list, mock_nav, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_nav.return_value = _mock_nav_result("Sequence")
        mock_list.return_value = _mock_list_result([
            ListEntry(
                object_type="Cue", object_id=1, name="Cue 1",
                columns={"Fade": "2.0", "Delay": "0.5"},
            ),
        ])

        from src.resources import register_resources
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        register_resources(mcp)

        result = await _call_resource_template(
            mcp, "gma2://show/sequences/{seq_id}/cues", seq_id="1"
        )
        data = json.loads(result)
        assert data["cues"][0]["columns"]["Fade"] == "2.0"


# ---------------------------------------------------------------------------
# parse_listvar (unit tests for shared helper)
# ---------------------------------------------------------------------------

class TestParseListvar:
    def test_standard_output(self):
        from src.tools import parse_listvar
        raw = (
            "[channel  ]Fixture>\n"
            "$Global : $SHOWFILE = my_show\n"
            "$Global : $VERSION = 3.9.60.65\n"
        )
        result = parse_listvar(raw)
        assert result == {"$SHOWFILE": "my_show", "$VERSION": "3.9.60.65"}

    def test_filter_prefix(self):
        from src.tools import parse_listvar
        raw = (
            "$Global : $SHOWFILE = my_show\n"
            "$Global : $VERSION = 3.9.60.65\n"
            "$Global : $SELECTEDEXEC = 1.1.1\n"
            "$Global : $SELECTEDEXECCUE = NONE\n"
        )
        result = parse_listvar(raw, filter_prefix="SELECTED")
        assert len(result) == 2
        assert "$SELECTEDEXEC" in result
        assert "$SELECTEDEXECCUE" in result

    def test_empty_input(self):
        from src.tools import parse_listvar
        assert parse_listvar("") == {}

    def test_prompt_lines_skipped(self):
        from src.tools import parse_listvar
        raw = "[channel  ]Fixture>\n"
        assert parse_listvar(raw) == {}


# ---------------------------------------------------------------------------
# Helpers: call registered resources directly
# ---------------------------------------------------------------------------

async def _call_resource(mcp: "FastMCP", uri: str) -> str:
    """Read a registered static resource by URI."""
    result = await mcp.read_resource(uri)
    # FastMCP returns list of content objects; first one has text
    if hasattr(result, '__iter__'):
        for item in result:
            if hasattr(item, 'text'):
                return item.text
            if hasattr(item, 'content'):
                return item.content
    return str(result)


async def _call_resource_template(mcp: "FastMCP", template_uri: str, **kwargs) -> str:
    """Read a resource template by substituting parameters."""
    # Build the concrete URI from the template
    concrete_uri = template_uri
    for key, value in kwargs.items():
        concrete_uri = concrete_uri.replace(f"{{{key}}}", value)
    return await _call_resource(mcp, concrete_uri)
