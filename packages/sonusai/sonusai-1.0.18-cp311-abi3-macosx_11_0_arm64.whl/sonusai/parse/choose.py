import pyparsing as pp

from ..utils.choice import RandomChoice


def parse_choose_expression(expression: str) -> RandomChoice:
    """
    Parse a string of the form "choose([1, 2, 3])" or "choose([1, 2, 3], repetition=True)"
    and return a RandomChoice object with the parsed list and optional repetition parameter.

    Args:
        expression: String to parse, e.g., "choose([1, 2, 3])" or "choose([1, 2, 3], repetition=False)"

    Returns:
        RandomChoice object with parsed data and repetition settings

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

    # Repetition parameter: repetition=True, or repetition=False
    repetition_param = pp.Keyword("repetition") + pp.Suppress("=") + boolean

    # Function call: choose([...]) or choose([...], repetition=...)
    function_call = (
        pp.Keyword("choose")
        + pp.Suppress("(")
        + list_def
        + pp.Optional(pp.Suppress(",") + repetition_param)
        + pp.Suppress(")")
    )

    # Parse the expression
    try:
        result = function_call.parseString(expression, parseAll=True)

        # Extract the list (everything between 'choose' and potential 'repetition')
        data_list = []
        repetition: bool = False

        for item in result:
            if item == "choose":
                continue
            elif item == "repetition":
                break
            else:
                data_list.append(item)

        # If repetition was specified, find its value
        if "repetition" in result.as_list():
            repetition_index = result.asList().index("repetition")
            if repetition_index + 1 < len(result):
                repetition = bool(result[repetition_index + 1])

        return RandomChoice(data_list, repetition=repetition)

    except pp.ParseException as e:
        raise pp.ParseException(f"Invalid choose expression format: {e}") from e
