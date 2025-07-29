"""
Parse 'expand' expressions.

This module provides functionality to find, parse and evaluate 'expand'
expressions in text, supporting nested expressions and random value generation.
"""

import re
from dataclasses import dataclass

import pyparsing as pp

# Constants
SAI_EXPAND_PATTERN = r"expand\("
SAI_RAND_LITERAL = "rand"
SAI_EXPAND_LITERAL = "expand"


@dataclass
class Match:
    """Represents a matched 'expand' expression in text."""

    group: str
    span: tuple[int, int]

    def start(self) -> int:
        """Return the start position of the match."""
        return self.span[0]

    def end(self) -> int:
        """Return the end position of the match."""
        return self.span[1]


def find_matching_parenthesis(text: str, start_pos: int) -> int:
    """Find the position of the matching closing parenthesis.

    :param text: The text to search in
    :param start_pos: Position after the opening parenthesis
    :return: Position after the matching closing parenthesis
    :raises ValueError: If no matching parenthesis is found
    """
    num_lparen = 1
    pos = start_pos

    while num_lparen != 0 and pos < len(text):
        if text[pos] == "(":
            num_lparen += 1
        elif text[pos] == ")":
            num_lparen -= 1
        pos += 1

    if num_lparen != 0:
        raise ValueError(f"Unbalanced parenthesis in '{text}'")

    return pos


def find_expand(text: str) -> list[Match]:
    """Find all 'expand' expressions in the text.

    :param text: The text to search in
    :return: List of Match objects for each 'expand' expression
    :raises ValueError: If parentheses are unbalanced
    """
    results = []
    matches = re.finditer(SAI_EXPAND_PATTERN, text)

    for match in matches:
        start = match.start()
        end_pos = find_matching_parenthesis(text, match.end())
        results.append(Match(group=text[start:end_pos], span=(start, end_pos)))

    return results


def create_parser() -> pp.ParserElement:
    """Create a pyparsing parser for 'expand' expressions.

    :return: Parser for 'expand' expressions
    """
    lparen = pp.Literal("(")
    rparen = pp.Literal(")")
    comma = pp.Literal(",")

    # Define numeric types
    real_number = pp.pyparsing_common.real
    signed_integer = pp.pyparsing_common.signed_integer
    number = real_number | signed_integer

    # Define identifiers and expressions
    identifier = pp.Word(pp.alphanums + "_.-")

    # Define 'rand' expression
    rand_literal = pp.Literal(SAI_RAND_LITERAL)
    rand_expression = (rand_literal + lparen + number + comma + number + rparen).set_parse_action(
        lambda tokens: "".join(map(str, tokens))
    )

    # Define 'expand' expression
    expand_literal = pp.Literal(SAI_EXPAND_LITERAL)
    expand_args = pp.DelimitedList(rand_expression | identifier, min=1)
    expand_expression = expand_literal + lparen + expand_args("args") + rparen

    return expand_expression


def parse_expand(text: str) -> list[str]:
    """Parse an 'expand' expression and extract its arguments.

    :param text: Text containing an 'expand' expression
    :return: List of argument values
    :raises ValueError: If the expression cannot be parsed
    """
    parser = create_parser()

    try:
        result = parser.parse_string(text)
        return list(result.args)
    except pp.ParseException as e:
        raise ValueError(f"Could not parse '{text}'") from e


def expand(directive: str) -> list[str]:
    """Evaluate the 'expand' directive.

    Recursively processes and expands 'expand' expressions in the text,
    starting with the innermost expressions.

    :param directive: Directive to evaluate
    :return: A list of the expanded results
    """
    # Initialize with input
    expanded = [directive]

    # Look for 'expand' patterns
    matches = find_expand(directive)

    # If no pattern found, return the original text
    if not matches:
        return expanded

    # Remove the original text as we'll replace it with expanded versions
    expanded.pop()

    # Start with the innermost match (last in the list)
    match = matches[-1]
    prelude = directive[: match.start()]
    postlude = directive[match.end() :]

    # Process each value in the 'expand' expression
    for value in parse_expand(match.group):
        # Recursively expand the text with each replacement value
        expanded.extend(expand(prelude + value + postlude))

    return expanded
