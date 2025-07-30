import pyparsing as pp

from ..utils.choice import SequentialChoice


def parse_sequence_expression(expression: str) -> SequentialChoice:
    """
    Parse a string of the form "sequence([1, 2, 3])"
    and return a SequentialChoice object with the parsed list.

    Args:
        expression: String to parse, e.g., "sequence([1, 2, 3])"

    Returns:
        SequentialChoice object with parsed data

    Raises:
        pp.ParseException: If the string doesn't match the expected format
    """
    # Define grammar for parsing numbers, strings, and booleans
    number = pp.pyparsing_common.number
    quoted_string = pp.QuotedString('"') | pp.QuotedString("'")
    boolean = pp.Keyword("True").setParseAction(lambda: True) | pp.Keyword("False").setParseAction(lambda: False)

    # List element can be a number, quoted string, or boolean
    list_element = number | quoted_string | boolean

    # List definition: [item1, item2, ...]
    list_def = pp.Suppress("[") + pp.Optional(pp.delimitedList(list_element)) + pp.Suppress("]")

    # Function call: sequence([...])
    function_call = pp.Keyword("sequence") + pp.Suppress("(") + list_def + pp.Suppress(")")

    # Parse the expression
    try:
        result = function_call.parseString(expression, parseAll=True)

        # Extract the list (everything after 'sequence')
        data_list = []

        for item in result:
            if item == "sequence":
                continue
            else:
                data_list.append(item)

        return SequentialChoice(data_list)

    except pp.ParseException as e:
        raise pp.ParseException(f"Invalid sequence expression format: {e}") from e
