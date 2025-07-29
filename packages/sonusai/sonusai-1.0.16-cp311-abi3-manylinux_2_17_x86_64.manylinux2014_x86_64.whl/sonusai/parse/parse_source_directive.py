from dataclasses import dataclass
from dataclasses import fields
from typing import Any

from pyparsing import Literal
from pyparsing import Optional
from pyparsing import ParseException
from pyparsing import ParseResults
from pyparsing import QuotedString
from pyparsing import Suppress
from pyparsing import Word
from pyparsing import ZeroOrMore
from pyparsing import alphanums
from pyparsing import alphas
from pyparsing import pyparsing_common


@dataclass
class SourceDirective:
    """Represents a parsed source directive with its parameters."""

    unique: str | None = None
    repeat: bool = False
    loop: bool = False
    start: int = 0


def parse_source_directive(directive: str) -> SourceDirective:
    """Parse a source directive into its components.

    Parses directives of the form:
    - choose(unique=None, repeat=False, loop=False, start=0)
    - sequence(unique=None, loop=False, start=0)

    :param directive: The directive string to parse
    :return: SourceDirective with parsed parameters
    :raises ValueError: If the directive format is invalid
    """
    # Check for a simple directive without parentheses
    if _is_simple_directive(directive):
        return SourceDirective()

    # Parse full directive with parameters
    parsed_tokens = _parse_directive_grammar(directive)
    params = _process_parsed_parameters(parsed_tokens, directive)

    return SourceDirective(**params)


def _get_valid_parameters() -> set[str]:
    """Get valid parameter names from SourceDirective dataclass fields."""
    return {field.name for field in fields(SourceDirective)}


def _is_simple_directive(directive: str) -> bool:
    """Check if the directive is just a function name without parentheses."""
    directive_type = Literal("choose") | Literal("sequence")
    try:
        directive_type.parseString(directive, parseAll=True)
    except ParseException:
        return False
    return True


def _parse_directive_grammar(directive: str) -> ParseResults:
    """Parse directive using pyparsing grammar and return tokens."""
    # Define grammar components
    directive_type = Literal("choose") | Literal("sequence")
    identifier = Word(alphas + "_", alphanums + "_")

    # Value types
    none_value = Literal("None")
    true_value = Literal("True")
    false_value = Literal("False")
    integer = pyparsing_common.signed_integer()
    quoted_string = QuotedString('"', escChar="\\") | QuotedString("'", escChar="\\")
    non_quoted_string = Word(alphanums + "_-./")
    rand_value = Literal("rand")

    # Combined value and parameter grammar
    value = none_value | true_value | false_value | integer | quoted_string | non_quoted_string | rand_value
    parameter = identifier + Suppress("=") + value
    param_list = Optional(parameter + ZeroOrMore(Suppress(",") + parameter) + Optional(Suppress(",")))
    directive_expr = Suppress(directive_type) + Suppress("(") + param_list + Suppress(")")

    try:
        return directive_expr.parseString(directive, parseAll=True)
    except ParseException as e:
        raise ValueError(f"Invalid directive format: '{directive}'. Error: {e}") from e


def _process_parsed_parameters(parsed_tokens: ParseResults, directive: str) -> dict:
    """Convert parsed tokens to a parameter dictionary with type conversion."""
    params = {}
    valid_params = _get_valid_parameters()

    for i in range(0, len(parsed_tokens), 2):
        param_name = parsed_tokens[i]
        param_value = parsed_tokens[i + 1]

        _validate_parameter_name(param_name, directive, valid_params)
        params[param_name] = _convert_parameter_value(param_value)

    return params


def _validate_parameter_name(param_name: Any, directive: str, valid_params: set[str]) -> None:
    """Validate that parameter name is allowed."""
    if param_name not in valid_params:
        raise ValueError(
            f"Invalid directive format: '{directive}'. Error: parameter must be one of {', '.join(sorted(valid_params))}."
        )


def _convert_parameter_value(param_value):
    """Convert string representations to appropriate Python types."""
    if param_value == "None":
        return None
    elif param_value in ("True", "true", "Yes", "yes"):
        return True
    elif param_value in ("False", "false", "No", "no"):
        return False
    elif param_value == "rand":
        return "rand"
    elif isinstance(param_value, int):
        return param_value
    else:
        # String value (already unquoted by pyparsing)
        return param_value
