"""sonusai

usage: sonusai [--version] [--help] <command> [<args>...]

The sonusai commands are:
    <This information is automatically generated.>

Aaware Sound and Voice Machine Learning Framework. See 'sonusai help <command>'
for more information on a specific command.

"""

import sys
from importlib import import_module
from pkgutil import iter_modules

from docopt import docopt

from sonusai import BASEDIR
from sonusai import __version__ as sai_version
from sonusai import commands_list
from sonusai import logger
from sonusai.utils.docstring import add_commands_to_docstring
from sonusai.utils.docstring import trim_docstring


def discover_plugins():
    plugins = {}
    plugin_docstrings = []
    for _, name, _ in iter_modules():
        if name.startswith("sonusai_") and not name.startswith("sonusai_asr_"):
            module = import_module(name)
            plugins[name] = {
                "commands": commands_list(module.commands_doc),
                "basedir": module.BASEDIR,
            }
            plugin_docstrings.append(module.commands_doc)
    return plugins, plugin_docstrings


def execute_command_direct(command: str, argv: list[str], basedir: str) -> None:
    """Execute a command by importing and running it directly."""
    try:
        # Add the command directory to the Python path temporarily
        if basedir not in sys.path:
            sys.path.insert(0, basedir)

        # Import the command module
        command_module = import_module(command)

        # Set up sys.argv as the command module expects it
        original_argv = sys.argv
        sys.argv = [command, *argv]

        try:
            # Execute the main function if it exists
            if hasattr(command_module, "main"):
                command_module.main()
            else:
                logger.error(f"Command module {command} has no main() function")
                sys.exit(1)
        finally:
            # Restore original sys.argv
            sys.argv = original_argv

    except ImportError as err:
        logger.error(f"Failed to import command module {command}: {err}")
        sys.exit(1)
    except Exception as err:
        logger.error(f"Error executing command {command}: {err}")
        sys.exit(1)


def handle_help_command_direct(argv: list[str], base_commands: list[str], plugins: dict) -> None:
    """Handle the help command by executing modules directly."""
    if not argv:
        # Show the main help by re-running with -h
        sys.argv = ["sonusai", "-h"]
        main()
        return

    help_target = argv[0]

    if help_target in base_commands:
        execute_command_direct(help_target, ["-h"], BASEDIR)
    else:
        for data in plugins.values():
            if help_target in data["commands"]:
                execute_command_direct(help_target, ["-h"], data["basedir"])
                return

        logger.error(f"{help_target} is not a SonusAI command. See 'sonusai help'.")
        sys.exit(1)


def main() -> None:
    plugins, plugin_docstrings = discover_plugins()
    updated_docstring = add_commands_to_docstring(__doc__, plugin_docstrings)
    args = docopt(
        trim_docstring(updated_docstring),
        version=sai_version,
        options_first=True,
    )

    command = args["<command>"]
    argv = args["<args>"]
    base_commands = commands_list()

    if command == "help":
        handle_help_command_direct(argv, base_commands, plugins)
        return

    if command in base_commands:
        execute_command_direct(command, argv, BASEDIR)
        return

    for data in plugins.values():
        if command in data["commands"]:
            execute_command_direct(command, argv, data["basedir"])
            return

    logger.error(f"{command} is not a SonusAI command. See 'sonusai help'.")
    sys.exit(1)


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils.keyboard_interrupt import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)
