def validate_asr_configs(given: dict) -> None:
    """Validate fields in 'asr_config' in the given config

    :param given: The dictionary of the given config
    """
    from ..utils.asr import validate_asr
    from .constants import REQUIRED_ASR_CONFIGS_FIELDS

    if "asr_configs" not in given:
        raise AttributeError("config is missing required 'asr_configs'")

    asr_configs = given["asr_configs"]

    for name, asr_config in asr_configs.items():
        for key in REQUIRED_ASR_CONFIGS_FIELDS:
            if key not in asr_config:
                raise AttributeError(f"'{name}' in asr_configs is missing required '{key}'")

        engine = asr_config["engine"]
        config = {x: asr_config[x] for x in asr_config if x != "engine"}
        validate_asr(engine, **config)
