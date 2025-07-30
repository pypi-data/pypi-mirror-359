from sonusai.datatypes import SourceFile


def update_sources(given: dict) -> dict:
    """Validate and update fields in given 'sources'

    :param given: The dictionary of the given config
    """
    from .constants import REQUIRED_NON_PRIMARY_SOURCE_CONFIG_FIELDS
    from .constants import REQUIRED_SOURCE_CONFIG_FIELDS
    from .constants import REQUIRED_SOURCES_CATEGORIES
    from .constants import VALID_NON_PRIMARY_SOURCE_CONFIG_FIELDS
    from .constants import VALID_PRIMARY_SOURCE_CONFIG_FIELDS

    sources = given["sources"]

    for category in REQUIRED_SOURCES_CATEGORIES:
        if category not in sources:
            raise AttributeError(f"config sources is missing required '{category}'")

    for category, source in sources.items():
        for key in REQUIRED_SOURCE_CONFIG_FIELDS:
            if key not in source:
                raise AttributeError(f"config source '{category}' is missing required '{key}'")

        if category == "primary":
            for key in source:
                if key not in VALID_PRIMARY_SOURCE_CONFIG_FIELDS:
                    nice_list = "\n".join([f"  {item}" for item in VALID_PRIMARY_SOURCE_CONFIG_FIELDS])
                    raise AttributeError(
                        f"Invalid source '{category}' config parameter: '{key}'.\nValid sources config parameters are:\n{nice_list}"
                    )
        else:
            for key in REQUIRED_NON_PRIMARY_SOURCE_CONFIG_FIELDS:
                if key not in source:
                    raise AttributeError(f"config source '{category}' is missing required '{key}'")

            for key in source:
                if key not in VALID_NON_PRIMARY_SOURCE_CONFIG_FIELDS:
                    nice_list = "\n".join([f"  {item}" for item in VALID_NON_PRIMARY_SOURCE_CONFIG_FIELDS])
                    raise AttributeError(
                        f"Invalid source '{category}' config parameter: '{key}'.\nValid source config parameters are:\n{nice_list}"
                    )

        files = source["files"]

        if isinstance(files, str) and files in sources and files != category:
            continue

        if isinstance(files, list):
            continue

        raise TypeError(
            f"'file' parameter of config source '{category}' is not a list or a reference to another source"
        )

    count = 0
    while any(isinstance(source["files"], str) for source in sources.values()) and count < 100:
        count += 1
        for category, source in sources.items():
            files = source["files"]
            if isinstance(files, str):
                given["sources"][category]["files"] = sources[files]["files"]

    if count == 100:
        raise RuntimeError("Check config sources for circular references")

    return given


def get_source_files(config: dict, show_progress: bool = False) -> list[SourceFile]:
    """Get the list of source files from a config

    :param config: Config dictionary
    :param show_progress: Show progress bar
    :return: List of source files
    """
    from itertools import chain

    from ..utils.parallel import par_track
    from ..utils.parallel import track

    sources = config["sources"]
    if not isinstance(sources, dict) and not all(isinstance(source, dict) for source in sources):
        raise TypeError("'sources' must be a dictionary of dictionaries")

    if "primary" not in sources:
        raise AttributeError("'primary' is missing in 'sources'")

    class_indices = config["class_indices"]
    if not isinstance(class_indices, list):
        class_indices = [class_indices]

    level_type = config["level_type"]

    source_files: list[SourceFile] = []
    for category in sources:
        source_files.extend(
            chain.from_iterable(
                [
                    append_source_files(
                        category=category,
                        entry=entry,
                        class_indices=class_indices,
                        truth_configs=sources[category].get("truth_configs", []),
                        level_type=level_type,
                    )
                    for entry in sources[category]["files"]
                ]
            )
        )

    progress = track(total=len(source_files), disable=not show_progress)
    source_files = par_track(_get_num_samples, source_files, progress=progress)
    progress.close()

    num_classes = config["num_classes"]
    for source_file in source_files:
        if any(class_index < 0 for class_index in source_file.class_indices):
            raise ValueError("class indices must contain only positive elements")

        if any(class_index > num_classes for class_index in source_file.class_indices):
            raise ValueError(f"class index elements must not be greater than {num_classes}")

    return source_files


def append_source_files(
    category: str,
    entry: dict,
    class_indices: list[int],
    truth_configs: dict,
    level_type: str,
    tokens: dict | None = None,
) -> list[SourceFile]:
    """Process source files list and append as needed

    :param category: Source file category name
    :param entry: Source file entry to append to the list
    :param class_indices: Class indices
    :param truth_configs: Truth configs
    :param level_type: Level type
    :param tokens: Tokens used for variable expansion
    :return: List of source files
    """
    from copy import deepcopy
    from glob import glob
    from os import listdir
    from os.path import dirname
    from os.path import isabs
    from os.path import isdir
    from os.path import join
    from os.path import splitext

    from ..datatypes import TruthConfig
    from ..mixture.audio import validate_input_file
    from ..utils.dataclass_from_dict import dataclass_from_dict
    from ..utils.tokenized_shell_vars import tokenized_expand
    from ..utils.tokenized_shell_vars import tokenized_replace
    from .constants import REQUIRED_TRUTH_CONFIG_FIELDS

    if tokens is None:
        tokens = {}

    truth_configs_merged = deepcopy(truth_configs)

    if not isinstance(entry, dict):
        raise TypeError("'entry' must be a dictionary")

    in_name = entry.get("name")
    if in_name is None:
        raise KeyError("Source file list contained record without name")

    class_indices = entry.get("class_indices", class_indices)
    if not isinstance(class_indices, list):
        class_indices = [class_indices]

    truth_configs_override = entry.get("truth_configs", {})
    for key in truth_configs_override:
        if key not in truth_configs:
            raise AttributeError(
                f"Truth config '{key}' override specified for {entry['name']} is not defined at top level"
            )
        if key in truth_configs_override:
            truth_configs_merged[key] |= truth_configs_override[key]

    level_type = entry.get("level_type", level_type)

    in_name, new_tokens = tokenized_expand(in_name)
    tokens.update(new_tokens)
    names = sorted(glob(in_name))
    if not names:
        raise OSError(f"Could not find {in_name}. Make sure path exists")

    source_files: list[SourceFile] = []
    for name in names:
        ext = splitext(name)[1].lower()
        dir_name = dirname(name)
        if isdir(name):
            for file in listdir(name):
                child = file
                if not isabs(child):
                    child = join(dir_name, child)
                source_files.extend(
                    append_source_files(
                        category=category,
                        entry={"name": child},
                        class_indices=class_indices,
                        truth_configs=truth_configs_merged,
                        level_type=level_type,
                        tokens=tokens,
                    )
                )
        else:
            try:
                if ext == ".txt":
                    with open(file=name) as txt_file:
                        for line in txt_file:
                            # strip comments
                            child = line.partition("#")[0]
                            child = child.rstrip()
                            if child:
                                child, new_tokens = tokenized_expand(child)
                                tokens.update(new_tokens)
                                if not isabs(child):
                                    child = join(dir_name, child)
                                source_files.extend(
                                    append_source_files(
                                        category=category,
                                        entry={"name": child},
                                        class_indices=class_indices,
                                        truth_configs=truth_configs_merged,
                                        level_type=level_type,
                                        tokens=tokens,
                                    )
                                )
                else:
                    validate_input_file(name)
                    source_file = SourceFile(
                        category=category,
                        name=tokenized_replace(name, tokens),
                        samples=0,
                        class_indices=class_indices,
                        level_type=level_type,
                        truth_configs={},
                    )
                    if len(truth_configs_merged) > 0:
                        for tc_key, tc_value in truth_configs_merged.items():
                            config = deepcopy(tc_value)
                            truth_config: dict = {}
                            for key in REQUIRED_TRUTH_CONFIG_FIELDS:
                                truth_config[key] = config[key]
                                del config[key]
                            truth_config["config"] = config
                            source_file.truth_configs[tc_key] = dataclass_from_dict(TruthConfig, truth_config)
                        for tc_key in source_file.truth_configs:
                            if (
                                "function" in truth_configs_merged[tc_key]
                                and truth_configs_merged[tc_key]["function"] == "file"
                            ):
                                truth_configs_merged[tc_key]["file"] = splitext(source_file.name)[0] + ".h5"
                    source_files.append(source_file)
            except Exception as e:
                raise OSError(f"Error processing {name}: {e}") from e

    return source_files


def _get_num_samples(entry: SourceFile) -> SourceFile:
    from ..mixture.audio import get_num_samples

    entry.samples = get_num_samples(entry.name)
    return entry


