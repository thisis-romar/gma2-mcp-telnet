"""
MCP Tools Tests

Tests for high-level MCP tools functionality. These are tools that AI can call.
Uses mocks to simulate Telnet connections and avoid actual network calls.

The MCP tool functions are defined in src/server.py with @mcp.tool() decorators.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestCreateFixtureGroupTool:
    """Tests for the create fixture group MCP tool."""

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_create_fixture_group_basic(self, mock_get_client):
        """Test creating a basic fixture group."""
        from src.server import create_fixture_group

        mock_client = MagicMock()
        mock_client.send_command = AsyncMock()
        mock_get_client.return_value = mock_client

        result = await create_fixture_group(start_fixture=1, end_fixture=10, group_id=1)

        calls = mock_client.send_command.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == "selfix fixture 1 thru 10"
        assert calls[1][0][0] == "store group 1"

        assert "Group 1" in result
        assert "Fixtures 1" in result
        assert "10" in result

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_create_fixture_group_with_label(self, mock_get_client):
        """Test creating a fixture group with a label."""
        from src.server import create_fixture_group

        mock_client = MagicMock()
        mock_client.send_command = AsyncMock()
        mock_get_client.return_value = mock_client

        result = await create_fixture_group(
            start_fixture=1, end_fixture=10, group_id=1, group_name="Front Wash"
        )

        calls = mock_client.send_command.call_args_list
        assert len(calls) == 3
        assert calls[0][0][0] == "selfix fixture 1 thru 10"
        assert calls[1][0][0] == "store group 1"
        assert calls[2][0][0] == 'label group 1 "Front Wash"'

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_create_fixture_group_with_custom_name(self, mock_get_client):
        """Test creating a fixture group with a custom name."""
        from src.server import create_fixture_group

        mock_client = MagicMock()
        mock_client.send_command = AsyncMock()
        mock_get_client.return_value = mock_client

        result = await create_fixture_group(
            start_fixture=1, end_fixture=10, group_id=1, group_name="Front Stage Wash"
        )

        calls = mock_client.send_command.call_args_list
        assert calls[2][0][0] == 'label group 1 "Front Stage Wash"'


class TestExecuteSequenceTool:
    """Tests for the execute sequence MCP tool."""

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_execute_sequence_go(self, mock_get_client):
        """Test executing a sequence (go)."""
        from src.server import execute_sequence

        mock_client = MagicMock()
        mock_client.send_command = AsyncMock()
        mock_get_client.return_value = mock_client

        result = await execute_sequence(sequence_id=1, action="go")

        mock_client.send_command.assert_called_once_with("go+ sequence 1")

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_execute_sequence_pause(self, mock_get_client):
        """Test pausing a sequence."""
        from src.server import execute_sequence

        mock_client = MagicMock()
        mock_client.send_command = AsyncMock()
        mock_get_client.return_value = mock_client

        result = await execute_sequence(sequence_id=1, action="pause")

        mock_client.send_command.assert_called_once_with("pause sequence 1")

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_execute_sequence_goto(self, mock_get_client):
        """Test jumping to a specific cue."""
        from src.server import execute_sequence

        mock_client = MagicMock()
        mock_client.send_command = AsyncMock()
        mock_get_client.return_value = mock_client

        result = await execute_sequence(sequence_id=1, action="goto", cue_id=5)

        mock_client.send_command.assert_called_once_with("goto cue 5 sequence 1")


class TestSendRawCommandTool:
    """Tests for the send raw command MCP tool."""

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_send_safe_write_command(self, mock_get_client):
        """Test sending a SAFE_WRITE command (selfix) — should be allowed."""
        from src.server import send_raw_command
        import json

        mock_client = MagicMock()
        mock_client.send_command_with_response = AsyncMock(return_value="[channel]>")
        mock_get_client.return_value = mock_client

        result = await send_raw_command("selfix fixture 1 thru 10")
        data = json.loads(result)

        mock_client.send_command_with_response.assert_called_once_with(
            "selfix fixture 1 thru 10"
        )
        assert data["command_sent"] == "selfix fixture 1 thru 10"
        assert data["blocked"] is False

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_block_destructive_command(self, mock_get_client):
        """Test that destructive commands are blocked without confirm_destructive."""
        from src.server import send_raw_command
        import json

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = await send_raw_command("delete cue 1 thru 9999")
        data = json.loads(result)

        assert data["blocked"] is True
        assert data["risk_tier"] == "DESTRUCTIVE"
        assert data["command_sent"] is None
        # Client should NOT have been called
        mock_client.send_command_with_response.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_allow_destructive_with_confirm(self, mock_get_client):
        """Test that destructive commands pass with confirm_destructive=True."""
        from src.server import send_raw_command
        import json

        mock_client = MagicMock()
        mock_client.send_command_with_response = AsyncMock(return_value="Ok")
        mock_get_client.return_value = mock_client

        result = await send_raw_command("store cue 1", confirm_destructive=True)
        data = json.loads(result)

        assert data["blocked"] is False
        assert data["command_sent"] == "store cue 1"
        assert data["risk_tier"] == "DESTRUCTIVE"

    @pytest.mark.asyncio
    async def test_block_command_injection(self):
        """Test that commands with line breaks are rejected."""
        from src.server import send_raw_command
        import json

        result = await send_raw_command("list\r\ndelete cue 1")
        data = json.loads(result)

        assert data["blocked"] is True
        assert "line breaks" in data["error"]
        assert data["command_sent"] is None

    @pytest.mark.asyncio
    @patch("src.server.get_client")
    async def test_safe_read_always_allowed(self, mock_get_client):
        """Test that SAFE_READ commands (list, info, cd) are always allowed."""
        from src.server import send_raw_command
        import json

        mock_client = MagicMock()
        mock_client.send_command_with_response = AsyncMock(return_value="[Fixture]>")
        mock_get_client.return_value = mock_client

        result = await send_raw_command("list")
        data = json.loads(result)

        assert data["blocked"] is False
        assert data["risk_tier"] == "SAFE_READ"
