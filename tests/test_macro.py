"""
Macro Commands Tests

Tests for grandMA2 macro placeholder command generation and
conditional execution syntax validation.

The @ character is used as a placeholder for user input in macros.
Conditional execution uses [$var == value] syntax (double equals).

Test Classes:
- TestMacroPlaceholder: Tests for macro_with_input_after, macro_with_input_before
- TestMacroCondition: Tests for macro_condition_line with operator validation
"""

import pytest



class TestMacroPlaceholder:
    """Tests for @ character macro placeholder."""

    def test_macro_with_input_after(self):
        """Test macro with @ at the end: Load @"""
        from src.commands import macro_with_input_after

        result = macro_with_input_after("Load")
        assert result == "Load @"

    def test_macro_with_input_after_complex(self):
        """Test macro with @ at the end for attribute: Attribute Pan At @"""
        from src.commands import macro_with_input_after

        result = macro_with_input_after("Attribute Pan At")
        assert result == "Attribute Pan At @"

    def test_macro_with_input_before(self):
        """Test macro with @ at the beginning: @ Fade 20"""
        from src.commands import macro_with_input_before

        result = macro_with_input_before("Fade 20")
        assert result == "@ Fade 20"


class TestMacroCondition:
    """Tests for macro conditional execution syntax [$var op value].

    grandMA2 macro conditions use == for equality, NOT single =.
    Single = is only for variable assignment (SetVar/AddVar).
    """

    # --- Valid condition tests ---

    def test_condition_equal(self):
        """Test condition with == operator: [$mymode == 1] Go Executor 1"""
        from src.commands import macro_condition_line

        result = macro_condition_line("$mymode", "==", 1, "Go Executor 1")
        assert result == "[$mymode == 1] Go Executor 1"

    def test_condition_not_equal(self):
        """Test condition with != operator."""
        from src.commands import macro_condition_line

        result = macro_condition_line("$counter", "!=", 0, "Go+ Macro 5")
        assert result == "[$counter != 0] Go+ Macro 5"

    def test_condition_less_than(self):
        """Test condition with < operator."""
        from src.commands import macro_condition_line

        result = macro_condition_line("$counter", "<", 10, "AddVar $counter + 1")
        assert result == "[$counter < 10] AddVar $counter + 1"

    def test_condition_greater_than(self):
        """Test condition with > operator."""
        from src.commands import macro_condition_line

        result = macro_condition_line("$counter", ">", 5, "Off Executor 1")
        assert result == "[$counter > 5] Off Executor 1"

    def test_condition_string_value(self):
        """Test condition with string value."""
        from src.commands import macro_condition_line

        result = macro_condition_line("$scene", "==", "intro", "Go Executor 1")
        assert result == "[$scene == intro] Go Executor 1"

    def test_condition_float_value(self):
        """Test condition with float value."""
        from src.commands import macro_condition_line

        result = macro_condition_line("$level", ">", 0.5, "Go Executor 1")
        assert result == "[$level > 0.5] Go Executor 1"

    # --- Telnet feedback validation tests ---

    def test_condition_output_matches_telnet_format(self):
        """Verify generated syntax matches grandMA2 telnet bracket format.

        The console expects exactly: [$varname == value] command
        with square brackets, spaces around operator, and space before command.
        """
        from src.commands import macro_condition_line

        result = macro_condition_line("$mymode", "==", 1, "Go Executor 1")
        # Must start with [ and contain ] before the command
        assert result.startswith("[")
        assert "] " in result
        # Must use double equals, never single
        condition_part = result.split("]")[0]
        assert " == " in condition_part
        assert condition_part.count("=") == 2  # Exactly two = chars

    def test_condition_loop_pattern(self):
        """Test self-calling macro loop pattern with condition.

        Common pattern: [$counter < N] Go+ Macro M (self-call for loop).
        """
        from src.commands import macro_condition_line

        result = macro_condition_line("$counter", "<", 5, "Go+ Macro 10")
        assert result == "[$counter < 5] Go+ Macro 10"

    def test_condition_reset_pattern(self):
        """Test counter reset at loop end: [$counter == N] SetVar $counter = 0"""
        from src.commands import macro_condition_line

        result = macro_condition_line("$counter", "==", 5, "SetVar $counter = 0")
        assert result == "[$counter == 5] SetVar $counter = 0"

    # --- Invalid operator tests (reject single =) ---

    def test_single_equals_rejected(self):
        """Single = must be rejected — it's for assignment (SetVar), not conditions."""
        from src.commands import macro_condition_line

        with pytest.raises(ValueError, match="Use '==' for equality"):
            macro_condition_line("$var", "=", 1, "Go Executor 1")

    def test_greater_equal_rejected(self):
        """grandMA2 does not support >= in macro conditions."""
        from src.commands import macro_condition_line

        with pytest.raises(ValueError, match="Invalid condition operator"):
            macro_condition_line("$var", ">=", 1, "Go Executor 1")

    def test_less_equal_rejected(self):
        """grandMA2 does not support <= in macro conditions."""
        from src.commands import macro_condition_line

        with pytest.raises(ValueError, match="Invalid condition operator"):
            macro_condition_line("$var", "<=", 1, "Go Executor 1")

    def test_triple_equals_rejected(self):
        """=== is not a valid grandMA2 operator."""
        from src.commands import macro_condition_line

        with pytest.raises(ValueError, match="Invalid condition operator"):
            macro_condition_line("$var", "===", 1, "Go Executor 1")

    # --- Edge case tests ---

    def test_empty_command_rejected(self):
        """Command must not be empty."""
        from src.commands import macro_condition_line

        with pytest.raises(ValueError, match="must not be empty"):
            macro_condition_line("$var", "==", 1, "")

    def test_whitespace_command_rejected(self):
        """Command must not be whitespace-only."""
        from src.commands import macro_condition_line

        with pytest.raises(ValueError, match="must not be empty"):
            macro_condition_line("$var", "==", 1, "   ")

    def test_var_without_dollar_rejected(self):
        """Variable name must start with $."""
        from src.commands import macro_condition_line

        with pytest.raises(ValueError, match="must start with"):
            macro_condition_line("myvar", "==", 1, "Go Executor 1")
