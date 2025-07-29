from importlib.resources import as_file
from importlib.resources import files

REQUIRED_CONFIGS: tuple[str, ...] = (
    "asr_configs",
    "class_balancing",
    "class_balancing_effect",
    "class_indices",
    "class_labels",
    "class_weights_threshold",
    "feature",
    "impulse_responses",
    "level_type",
    "mixture_effects",
    "num_classes",
    "seed",
    "sources",
    "spectral_masks",
    "summed_source_effects",
)
OPTIONAL_CONFIGS: tuple[str, ...] = ()
VALID_CONFIGS: tuple[str, ...] = REQUIRED_CONFIGS + OPTIONAL_CONFIGS

REQUIRED_SOURCES_CATEGORIES: tuple[str, ...] = (
    "primary",
    "noise",
)

REQUIRED_SOURCE_CONFIG_FIELDS: tuple[str, ...] = (
    "effects",
    "files",
)
OPTIONAL_SOURCE_CONFIG_FIELDS: tuple[str, ...] = ("truth_configs",)
REQUIRED_NON_PRIMARY_SOURCE_CONFIG_FIELDS: tuple[str, ...] = (
    "mix_rules",
    "snrs",
)
VALID_PRIMARY_SOURCE_CONFIG_FIELDS: tuple[str, ...] = REQUIRED_SOURCE_CONFIG_FIELDS + OPTIONAL_SOURCE_CONFIG_FIELDS
VALID_NON_PRIMARY_SOURCE_CONFIG_FIELDS: tuple[str, ...] = (
    VALID_PRIMARY_SOURCE_CONFIG_FIELDS + REQUIRED_NON_PRIMARY_SOURCE_CONFIG_FIELDS
)

REQUIRED_TRUTH_CONFIGS: tuple[str, ...] = (
    "function",
    "stride_reduction",
)

REQUIRED_ASR_CONFIGS_FIELDS: tuple[str, ...] = ("engine",)

REQUIRED_TRUTH_CONFIG_FIELDS = ["function", "stride_reduction"]

with as_file(files("sonusai.config").joinpath("config.yml")) as path:
    DEFAULT_CONFIG = str(path)
