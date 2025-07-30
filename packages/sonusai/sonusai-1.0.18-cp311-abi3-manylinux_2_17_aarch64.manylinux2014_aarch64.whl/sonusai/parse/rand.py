"""
Parse 'rand' expressions.

"""

import decimal
import re
from random import uniform

import pyparsing as pp

SIGNIFICANT_DIGITS = 6


def rand(directive: str) -> str:
    """Evaluate the 'rand(min, max)' directive and validate its syntax.

    :param directive: Directive to evaluate
    :return: Text with all 'rand' directives replaced with a random value,
                with a certain number of significant digits, or an empty string if 'text' is empty or None.
    :raises ValueError: If the expression cannot be parsed or is malformed.
    """
    if not directive:
        return directive

    # Create a recursive grammar for correct expressions
    expr = pp.Forward()
    number = pp.pyparsing_common.number

    func_name = pp.Literal("rand")
    left_paren = pp.Literal("(").suppress()
    right_paren = pp.Literal(")").suppress()
    comma = pp.Literal(",").suppress()

    # Allow whitespace around function parameters
    rand_function = (
        func_name
        + left_paren
        + pp.Optional(pp.White()).suppress()
        + (number | expr)("min_val")
        + pp.Optional(pp.White()).suppress()
        + comma
        + pp.Optional(pp.White()).suppress()
        + (number | expr)("max_val")
        + pp.Optional(pp.White()).suppress()
        + right_paren
    )

    # Complete the recursive definition
    expr << rand_function  # pyright: ignore [reportUnusedExpression]

    # Define parse action for generating random values
    def replace_with_random(tokens):
        min_val_token = tokens["min_val"]
        max_val_token = tokens["max_val"]

        # Convert tokens to float, handling both direct values and strings
        min_val = float(min_val_token)
        max_val = float(max_val_token)

        # Validate min/max relationship
        if min_val > max_val:
            raise ValueError(f"Min value ({min_val}) cannot be greater than max value ({max_val})")

        # Generate random value
        value = uniform(min_val, max_val)  # noqa: S311
        decimal.getcontext().prec = SIGNIFICANT_DIGITS
        return str(decimal.Decimal(value).normalize())

    rand_function.setParseAction(replace_with_random)

    # Create a validator parser for syntax checking only.
    # This parser doesn't transform but just validates the syntax.
    validator = pp.Forward()
    validator_rand = (
        func_name
        + left_paren
        + pp.Optional(pp.White()).suppress()
        + (number | validator)
        + pp.Optional(pp.White()).suppress()
        + comma
        + pp.Optional(pp.White()).suppress()
        + (number | validator)
        + pp.Optional(pp.White()).suppress()
        + right_paren
    )
    validator << validator_rand  # pyright: ignore [reportUnusedExpression]

    try:
        # First, try to validate all 'rand' expressions without evaluating them.
        # This helps identify structural problems before evaluation.
        malformations = []

        # Find all potential 'rand' expressions with or without opening/closing parentheses
        potential_expressions = list(re.finditer(r"rand\s*(\()?(?:[^()]|\([^()]*\))*\)?", directive))

        for match in potential_expressions:
            expr_text = match.group(0)

            # Check for missing opening parenthesis
            if "rand" in expr_text and "(" not in expr_text:
                malformations.append(f"Missing opening parenthesis in '{expr_text}'")
                continue

            # Check for missing closing parenthesis
            if not expr_text.endswith(")"):
                malformations.append(f"Missing closing parenthesis in '{expr_text}'")
                continue

            # Try to validate the expression structure
            try:
                validator.parseString(expr_text, parseAll=True)
            except pp.ParseException:
                # Count commas to check for parameter issues
                param_text = expr_text[expr_text.find("(") + 1 : expr_text.rfind(")")]

                # Track parenthesis nesting level to count commas correctly
                nesting_level = 0
                comma_count = 0

                for char in param_text:
                    if char == "(":
                        nesting_level += 1
                    elif char == ")":
                        nesting_level -= 1
                    elif char == "," and nesting_level == 0:
                        comma_count += 1

                if comma_count == 0:
                    if not param_text.strip():
                        malformations.append(f"Missing parameters in '{expr_text}' (expected 2)")
                    else:
                        # Check if there might be a space instead of comma
                        if re.search(r"\d+\s+[-+]?\d+", param_text):
                            malformations.append(f"Missing comma between parameters in '{expr_text}'")
                        else:
                            malformations.append(f"Too few parameters in '{expr_text}' (expected 2, got 1)")
                elif comma_count > 1:
                    malformations.append(f"Too many parameters in '{expr_text}' (expected 2, got {comma_count + 1})")
                else:
                    # There's 1 comma, so we have 2 parameters, but still a parsing error
                    # This is likely a non-numeric parameter
                    params = [p.strip() for p in split_params_respecting_nesting(param_text)]

                    for i, param in enumerate(params):
                        # Check nested 'rand' expressions for validity
                        if "rand" in param:
                            # Check if the nested expression is valid by recursively calling 'rand'
                            try:
                                # We only want to validate, not transform
                                nested_validator = pp.Forward()
                                nested_validator_rand = (
                                    func_name
                                    + left_paren
                                    + pp.Optional(pp.White()).suppress()
                                    + (number | nested_validator)
                                    + pp.Optional(pp.White()).suppress()
                                    + comma
                                    + pp.Optional(pp.White()).suppress()
                                    + (number | nested_validator)
                                    + pp.Optional(pp.White()).suppress()
                                    + right_paren
                                )
                                nested_validator << nested_validator_rand  # pyright: ignore [reportUnusedExpression]
                                nested_validator.parseString(param, parseAll=True)
                            except pp.ParseException:
                                malformations.append(f"Invalid nested expression '{param}' in '{expr_text}'")
                            continue

                        # Check if the parameter is numeric
                        if not is_numeric(param):
                            param_name = "first" if i == 0 else "second"
                            malformations.append(f"Non-numeric {param_name} parameter '{param}' in '{expr_text}'")

        if malformations:
            raise ValueError(f"Malformed rand directive: {'; '.join(malformations)}")

        # If validation passes, try to transform
        result = rand_function.transformString(directive)
    except pp.ParseException as e:
        raise ValueError(f"Invalid rand expression in '{directive}': {e!s}") from e

    return result


def is_numeric(text: str) -> bool:
    """Check if the text is a valid number (including scientific notation)."""
    numeric_pattern = r"^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$"
    return bool(re.match(numeric_pattern, text))


def split_params_respecting_nesting(param_text: str) -> list:
    """Split parameters by comma while respecting nested parentheses."""
    result = []
    current_param = []
    nesting_level = 0

    for char in param_text:
        if char == "(":
            nesting_level += 1
            current_param.append(char)
        elif char == ")" and nesting_level > 0:
            nesting_level -= 1
            current_param.append(char)
        elif char == "," and nesting_level == 0:
            result.append("".join(current_param))
            current_param = []
        else:
            current_param.append(char)

    if current_param:
        result.append("".join(current_param))

    return result
