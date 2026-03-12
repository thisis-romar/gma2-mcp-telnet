"""Tests for MCP Prompts (src/prompts.py).

All tests mock get_client() — no live console needed.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp.server.fastmcp import FastMCP
from src.prompts import register_prompts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mcp() -> FastMCP:
    """Create a fresh FastMCP instance with prompts registered."""
    mcp = FastMCP("test")
    register_prompts(mcp)
    return mcp


async def _get_prompt(mcp: FastMCP, name: str, arguments: dict | None = None) -> list:
    """Call a registered prompt and return the message list."""
    result = await mcp.get_prompt(name, arguments=arguments)
    # FastMCP returns a GetPromptResult; extract messages
    if hasattr(result, "messages"):
        return [{"role": m.role, "content": m.content.text} for m in result.messages]
    return result


# ---------------------------------------------------------------------------
# program-color-chase
# ---------------------------------------------------------------------------

class TestProgramColorChasePrompt:
    @pytest.mark.asyncio
    async def test_returns_message_list(self):
        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "program-color-chase")
        assert len(messages) >= 1
        assert messages[0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_includes_fixture_group(self):
        mcp = _make_mcp()
        messages = await _get_prompt(
            mcp, "program-color-chase",
            arguments={"fixture_group": "5", "color_count": "3"},
        )
        content = messages[0]["content"]
        assert "group 5" in content
        assert "3 colors" in content

    @pytest.mark.asyncio
    async def test_mentions_clear_programmer(self):
        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "program-color-chase")
        assert "clear_programmer" in messages[0]["content"]


# ---------------------------------------------------------------------------
# setup-moving-lights
# ---------------------------------------------------------------------------

class TestSetupMovingLightsPrompt:
    @pytest.mark.asyncio
    async def test_returns_message(self):
        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "setup-moving-lights")
        assert len(messages) >= 1
        assert messages[0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_includes_parameters(self):
        mcp = _make_mcp()
        messages = await _get_prompt(
            mcp, "setup-moving-lights",
            arguments={"fixture_type": "Robe Robin", "count": "12", "start_address": "101"},
        )
        content = messages[0]["content"]
        assert "12" in content
        assert "Robe Robin" in content
        assert "101" in content


# ---------------------------------------------------------------------------
# troubleshoot-connectivity
# ---------------------------------------------------------------------------

class TestTroubleshootConnectivityPrompt:
    @pytest.mark.asyncio
    async def test_returns_diagnostic_steps(self):
        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "troubleshoot-connectivity")
        content = messages[0]["content"]
        assert "list_system_variables" in content
        assert "Telnet" in content

    @pytest.mark.asyncio
    async def test_mentions_common_issues(self):
        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "troubleshoot-connectivity")
        content = messages[0]["content"]
        assert "Connection refused" in content
        assert "preserve_connectivity" in content


# ---------------------------------------------------------------------------
# create-cue-sequence
# ---------------------------------------------------------------------------

class TestCreateCueSequencePrompt:
    @pytest.mark.asyncio
    async def test_returns_workflow(self):
        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "create-cue-sequence")
        assert len(messages) >= 1
        content = messages[0]["content"]
        assert "store_cue" in content

    @pytest.mark.asyncio
    async def test_uses_parameters(self):
        mcp = _make_mcp()
        messages = await _get_prompt(
            mcp, "create-cue-sequence",
            arguments={"sequence_id": "99", "cue_count": "10"},
        )
        content = messages[0]["content"]
        assert "99" in content
        assert "10" in content


# ---------------------------------------------------------------------------
# show-status-report (dynamic)
# ---------------------------------------------------------------------------

class TestShowStatusReportPrompt:
    @pytest.mark.asyncio
    @patch("src.prompts.get_client")
    async def test_includes_live_state(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.send_command_with_response = AsyncMock(return_value=(
            "$Global : $SHOWFILE = test_show\n"
            "$Global : $VERSION = 3.9.60.65\n"
            "$Global : $USER = administrator\n"
        ))
        mock_get_client.return_value = mock_client

        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "show-status-report")
        content = messages[0]["content"]
        assert "test_show" in content
        assert "3.9.60.65" in content

    @pytest.mark.asyncio
    @patch("src.prompts.get_client")
    async def test_graceful_degradation_on_connection_failure(self, mock_get_client):
        mock_get_client.side_effect = ConnectionError("Console offline")

        mcp = _make_mcp()
        messages = await _get_prompt(mcp, "show-status-report")
        content = messages[0]["content"]
        assert "unavailable" in content
        assert "troubleshoot" in content.lower()
