from sonusai.datatypes import TruthParameter


def validate_truth_configs(given: dict) -> None:
    """Validate fields in given 'truth_configs'

    :param given: The dictionary of the given config
    """
    from copy import deepcopy

    from ..mixture import truth_functions
    from .constants import REQUIRED_TRUTH_CONFIGS

    sources = given["sources"]

    for category, source in sources.items():
        if "truth_configs" not in source:
            continue

        truth_configs = source["truth_configs"]
        if len(truth_configs) == 0:
            raise ValueError(f"'truth_configs' in config source '{category}' is empty")

        for truth_name, truth_config in truth_configs.items():
            for k in REQUIRED_TRUTH_CONFIGS:
                if k not in truth_config:
                    raise AttributeError(
                        f"'{truth_name}' in source '{category}' truth_configs is missing required '{k}'"
                    )

            optional_config = deepcopy(truth_config)
            for k in REQUIRED_TRUTH_CONFIGS:
                del optional_config[k]

            getattr(truth_functions, truth_config["function"] + "_validate")(optional_config)


def get_truth_parameters(config: dict) -> list[TruthParameter]:
    """Get the list of truth parameters from a config

    :param config: Config dictionary
    :return: List of truth parameters
    """
    from copy import deepcopy

    from ..mixture import truth_functions
    from .constants import REQUIRED_TRUTH_CONFIGS

    truth_parameters: list[TruthParameter] = []
    for category, source_config in config["sources"].items():
        if "truth_configs" in source_config:
            for truth_name, truth_config in source_config["truth_configs"].items():
                optional_config = deepcopy(truth_config)
                for key in REQUIRED_TRUTH_CONFIGS:
                    del optional_config[key]

                parameters = getattr(truth_functions, truth_config["function"] + "_parameters")(
                    config["feature"],
                    config["num_classes"],
                    optional_config,
                )
                truth_parameters.append(TruthParameter(category, truth_name, parameters))

    return truth_parameters
