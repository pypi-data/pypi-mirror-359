from sonusai.datatypes import SpectralMask


def get_spectral_masks(config: dict) -> list[SpectralMask]:
    """Get the list of spectral masks from a config

    :param config: Config dictionary
    :return: List of spectral masks
    """
    from ..utils.dataclass_from_dict import list_dataclass_from_dict

    try:
        return list_dataclass_from_dict(list[SpectralMask], config["spectral_masks"])
    except Exception as e:
        raise ValueError(f"Error in spectral_masks: {e}") from e
