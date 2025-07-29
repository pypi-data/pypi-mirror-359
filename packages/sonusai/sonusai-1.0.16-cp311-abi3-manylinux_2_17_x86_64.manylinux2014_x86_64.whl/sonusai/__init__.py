import atexit
import logging
from os.path import dirname

from rich.logging import RichHandler

from sonusai.rs import __version__ as rs_version

__version__ = rs_version

BASEDIR = dirname(__file__)

commands_doc = """
   audiofe                      Audio front end
   calc_metric_spenh            Run speech enhancement and analysis
   doc                          Documentation
   genft                        Generate feature and truth data
   genmetrics                   Generate mixture metrics data
   genmix                       Generate mixture and truth data
   genmixdb                     Generate a mixture database
   lsdb                         List information about a mixture database
   metrics_summary              Summarize generated metrics in a mixture database
   mkwav                        Make WAV files from a mixture database
   onnx_predict                 Run ONNX predict on a trained model
   vars                         List custom SonusAI variables
"""

# Global handler registry to prevent duplicates
_file_handlers = []


def _cleanup_handlers():
    """Clean up file handlers on exit"""
    for handler in _file_handlers:
        handler.close()


atexit.register(_cleanup_handlers)


def setup_logger(name: str = "sonusai") -> logging.Logger:
    """Setup and return configured logger"""
    _logger = logging.getLogger(name)

    # Avoid duplicate configuration
    if _logger.handlers:
        return _logger

    _logger.setLevel(logging.DEBUG)

    # Setup console handler
    formatter = logging.Formatter("%(message)s")

    console_handler = RichHandler(show_level=False, show_path=False, show_time=False)

    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    return _logger


# Initialize loggers
logger = setup_logger("sonusai")
logger_db = setup_logger("sonusai_db")


def create_file_handler(filename: str, verbose: bool = False) -> None:
    """Create a file handler with error handling"""
    from pathlib import Path

    try:
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter("%(message)s")
        formatter_db = logging.Formatter("%(asctime)s %(message)s")

        fh = logging.FileHandler(filename=filename, mode="w")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        _file_handlers.append(fh)

        if verbose:
            filename_db = Path(filename)
            filename_db = filename_db.parent / (filename_db.stem + "_dbtrace" + filename_db.suffix)
            fh_db = logging.FileHandler(filename=filename_db, mode="w")
            fh_db.setLevel(logging.DEBUG)
            fh_db.setFormatter(formatter_db)
            logger_db.addHandler(fh_db)
            _file_handlers.append(fh_db)

    except (PermissionError, OSError) as e:
        logger.warning(f"Could not create log file {filename}: {e}")


def update_console_handler(verbose: bool) -> None:
    """Update console handler verbosity"""
    console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler | RichHandler)]

    if not console_handlers:
        return

    handler = console_handlers[0]
    if not verbose:
        handler.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.DEBUG)


def initial_log_messages(name: str, subprocess: str | None = None) -> None:
    """Write initial log messages with error handling"""
    from datetime import datetime
    from getpass import getuser
    from os import getcwd
    from socket import gethostname
    from sys import argv

    try:
        if subprocess is None:
            logger.info(f"SonusAI {__version__}")
        else:
            logger.info(f"SonusAI {subprocess}")
        logger.info(f"{name}")
        logger.info("")
        logger.debug(f"Host:      {gethostname()}")
        logger.debug(f"User:      {getuser()}")
        logger.debug(f"Directory: {getcwd()}")
        logger.debug(f"Date:      {datetime.now()}")
        logger.debug(f"Command:   {' '.join(argv)}")
        logger.debug("")
    except Exception as e:
        logger.warning(f"Could not write initial log messages: {e}")


def commands_list(doc: str = commands_doc) -> list[str]:
    """Parse commands from a documentation string"""
    commands = []
    for line in doc.strip().split("\n"):
        line = line.strip()
        if line:
            # Get the first word that's not empty
            parts = line.split()
            if parts:
                commands.append(parts[0])
    return commands


def exception_handler(e: Exception) -> None:
    """Handle exceptions with proper logging"""
    import sys

    logger.error(f"{type(e).__name__}: {e}")

    # Find file handlers for detailed logs
    file_handlers = [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]

    if file_handlers:
        filenames = [handler.baseFilename for handler in file_handlers]
        logger.error(f"See {', '.join(filenames)} for details")

    from rich.console import Console

    console = Console(color_system=None)
    with console.capture() as capture:
        console.print_exception(show_locals=False)
    logger.debug(capture.get())

    sys.exit(1)
