from sonusai.datatypes import ImpulseResponseFile


def get_ir_files(config: dict, show_progress: bool = False) -> list[ImpulseResponseFile]:
    """Get the list of impulse response files from a config

    :param config: Config dictionary
    :param show_progress: Show progress bar
    :return: List of impulse response files
    """
    from itertools import chain

    from ..utils.parallel import par_track
    from ..utils.parallel import track

    ir_files = list(
        chain.from_iterable(
            [
                append_ir_files(
                    entry=ImpulseResponseFile(
                        name=entry["name"],
                        tags=entry.get("tags", []),
                        delay=entry.get("delay", "auto"),
                    )
                )
                for entry in config["impulse_responses"]
            ]
        )
    )

    if len(ir_files) == 0:
        return []

    progress = track(total=len(ir_files), disable=not show_progress)
    ir_files = par_track(_get_ir_delay, ir_files, progress=progress)
    progress.close()

    return ir_files


def append_ir_files(entry: ImpulseResponseFile, tokens: dict | None = None) -> list[ImpulseResponseFile]:
    """Process impulse response files list and append as needed

    :param entry: Impulse response file entry to append to the list
    :param tokens: Tokens used for variable expansion
    :return: List of impulse response files
    """
    from glob import glob
    from os import listdir
    from os.path import dirname
    from os.path import isabs
    from os.path import isdir
    from os.path import join
    from os.path import splitext

    from ..mixture.audio import validate_input_file
    from ..utils.tokenized_shell_vars import tokenized_expand
    from ..utils.tokenized_shell_vars import tokenized_replace
    from .config import load_yaml

    if tokens is None:
        tokens = {}

    in_name, new_tokens = tokenized_expand(entry.name)
    tokens.update(new_tokens)
    names = sorted(glob(in_name))
    if not names:
        raise OSError(f"Could not find {in_name}. Make sure path exists")

    ir_files: list[ImpulseResponseFile] = []
    for name in names:
        ext = splitext(name)[1].lower()
        dir_name = dirname(name)
        if isdir(name):
            for file in listdir(name):
                if not isabs(file):
                    file = join(dir_name, file)
                child = ImpulseResponseFile(file, entry.tags, entry.delay)
                ir_files.extend(append_ir_files(entry=child, tokens=tokens))
        else:
            try:
                if ext == ".txt":
                    with open(file=name) as txt_file:
                        for line in txt_file:
                            # strip comments
                            file = line.partition("#")[0]
                            file = file.rstrip()
                            if file:
                                file, new_tokens = tokenized_expand(file)
                                tokens.update(new_tokens)
                                if not isabs(file):
                                    file = join(dir_name, file)
                                child = ImpulseResponseFile(file, entry.tags, entry.delay)
                                ir_files.extend(append_ir_files(entry=child, tokens=tokens))
                elif ext == ".yml":
                    try:
                        yml_config = load_yaml(name)

                        if "impulse_responses" in yml_config:
                            for record in yml_config["impulse_responses"]:
                                ir_files.extend(append_ir_files(entry=record, tokens=tokens))
                    except Exception as e:
                        raise OSError(f"Error processing {name}: {e}") from e
                else:
                    validate_input_file(name)
                    ir_files.append(ImpulseResponseFile(tokenized_replace(name, tokens), entry.tags, entry.delay))
            except Exception as e:
                raise OSError(f"Error processing {name}: {e}") from e

    return ir_files


def _get_ir_delay(entry: ImpulseResponseFile) -> ImpulseResponseFile:
    from .ir_delay import get_ir_delay

    if entry.delay == "auto":
        entry.delay = get_ir_delay(entry.name)
    else:
        try:
            entry.delay = int(entry.delay)
        except ValueError as e:
            raise ValueError(f"Invalid impulse response delay: {entry.delay}") from e

    return entry
