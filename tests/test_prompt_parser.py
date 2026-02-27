"""
Tests for grandMA2 telnet prompt parser.

Since the exact MA2 telnet prompt format is not yet validated against a live
console, these tests cover hypothesized patterns and edge cases.  The parser
is designed to be refined as real output is captured.
"""

import pytest

from src.prompt_parser import ConsolePrompt, parse_prompt, _split_location


# =========================================================================
# ConsolePrompt dataclass
# =========================================================================


class TestConsolePromptDataclass:
    def test_minimal(self):
        p = ConsolePrompt(raw_response="output")
        assert p.raw_response == "output"
        assert p.prompt_line is None
        assert p.location is None
        assert p.object_type is None
        assert p.object_id is None

    def test_full(self):
        p = ConsolePrompt(
            raw_response="raw",
            prompt_line="[Group 1]>",
            location="Group 1",
            object_type="Group",
            object_id="1",
        )
        assert p.location == "Group 1"
        assert p.object_type == "Group"
        assert p.object_id == "1"

    def test_frozen(self):
        p = ConsolePrompt(raw_response="test")
        with pytest.raises(AttributeError):
            p.raw_response = "changed"


# =========================================================================
# Bracket pattern: [Location]> or [Location]>/
# =========================================================================


class TestBracketPromptPattern:
    def test_object_with_id(self):
        result = parse_prompt("some output\n[Group 1]>")
        assert result.prompt_line == "[Group 1]>"
        assert result.location == "Group 1"
        assert result.object_type == "Group"
        assert result.object_id == "1"

    def test_object_without_id(self):
        result = parse_prompt("[Fixture]>")
        assert result.location == "Fixture"
        assert result.object_type == "Fixture"
        assert result.object_id is None

    def test_root(self):
        result = parse_prompt("[Root]>")
        assert result.location == "Root"
        assert result.object_type == "Root"
        assert result.object_id is None

    def test_channel_default_prompt(self):
        result = parse_prompt("[channel]>")
        assert result.location == "channel"
        assert result.object_type == "channel"
        assert result.object_id is None

    def test_with_trailing_slash(self):
        result = parse_prompt("[Sequence 3]>/")
        assert result.location == "Sequence 3"
        assert result.object_type == "Sequence"
        assert result.object_id == "3"

    def test_with_preceding_output(self):
        raw = "OK\nSome output line\n[Sequence 3]>"
        result = parse_prompt(raw)
        assert result.location == "Sequence 3"
        assert result.object_type == "Sequence"
        assert result.object_id == "3"

    def test_multiline_with_prompt_at_end(self):
        raw = "Entering Group...\nStatus: OK\n[Group 1]>"
        result = parse_prompt(raw)
        assert result.location == "Group 1"

    def test_uses_last_match(self):
        """If multiple bracket prompts exist, use the last one."""
        raw = "[Root]>\ncd Group 1\n[Group 1]>"
        result = parse_prompt(raw)
        assert result.location == "Group 1"


# =========================================================================
# Generic angle-bracket pattern: something>
# =========================================================================


class TestAngleBracketPattern:
    def test_simple_prompt(self):
        result = parse_prompt("Root>")
        assert result.prompt_line == "Root>"
        assert result.location == "Root"
        assert result.object_type == "Root"

    def test_prompt_with_space(self):
        result = parse_prompt("Group 1>")
        assert result.location == "Group 1"
        assert result.object_type == "Group"
        assert result.object_id == "1"


# =========================================================================
# Edge cases
# =========================================================================


class TestEdgeCases:
    def test_empty_string(self):
        result = parse_prompt("")
        assert result.raw_response == ""
        assert result.prompt_line is None
        assert result.location is None

    def test_whitespace_only(self):
        result = parse_prompt("   \n  \n  ")
        assert result.prompt_line is None

    def test_no_recognizable_prompt(self):
        result = parse_prompt("Error: invalid command")
        assert result.raw_response == "Error: invalid command"
        # Falls through to angle-bracket pattern (no > found)
        assert result.prompt_line is None or result.location is None

    def test_raw_always_preserved(self):
        raw = "line1\nline2\n[Group 1]>"
        result = parse_prompt(raw)
        assert result.raw_response == raw


# =========================================================================
# _split_location helper
# =========================================================================


class TestSplitLocation:
    def test_type_and_id(self):
        assert _split_location("Group 1") == ("Group", "1")

    def test_type_only(self):
        assert _split_location("Fixture") == ("Fixture", None)

    def test_empty_string(self):
        assert _split_location("") == (None, None)

    def test_non_alpha_start(self):
        """Strings not starting with a letter don't match."""
        assert _split_location("123") == (None, None)

    def test_multi_word_type(self):
        """Only single-word types are recognized."""
        assert _split_location("some thing else") == (None, None)
