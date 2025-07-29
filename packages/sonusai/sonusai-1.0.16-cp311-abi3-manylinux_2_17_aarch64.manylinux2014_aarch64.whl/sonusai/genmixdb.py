"""sonusai genmixdb

usage: genmixdb [-hvmdjn] LOC

options:
    -h, --help
    -v, --verbose   Be verbose.
    -m, --mix       Save mixture data. [default: False].
    -d, --dryrun    Perform a dry run showing the processed config. [default: False].
    -j, --json      Save JSON version of database. [default: False].
    -n, --nopar     Do not run in parallel. [default: False].

Create mixture database data for training and evaluation. Optionally, also create mixture audio and feature/truth data.

genmixdb creates a database of training and evaluation feature and truth data generation information. It allows the
choice of audio neural-network feature types that are supported by the Aaware real-time front-end and truth data that is
synchronized frame-by-frame with the feature data.

For details, see sonusai doc.

"""

from functools import partial
from random import seed

import yaml

from sonusai import logger
from sonusai.constants import SAMPLE_RATE
from sonusai.datatypes import Mixture
from sonusai.mixture import MixtureDatabase
from sonusai.mixture.data_io import write_cached_data
from sonusai.mixture.generation import DatabaseManager
from sonusai.mixture.generation import update_mixture
from sonusai.mixture.helpers import write_mixture_metadata
from sonusai.mixture.log_duration_and_sizes import log_duration_and_sizes
from sonusai.utils.parallel import par_track
from sonusai.utils.parallel import track


def genmixdb(
    location: str,
    save_mix: bool = False,
    logging: bool = True,
    show_progress: bool = False,
    test: bool = False,
    verbose: bool = False,
    save_json: bool = False,
    no_par: bool = False,
) -> None:
    dbm = DatabaseManager(location, test, verbose, logging)
    mixdb = MixtureDatabase(location, test)

    dbm.populate_top_table()
    dbm.populate_class_label_table()
    dbm.populate_class_weights_threshold_table()
    dbm.populate_spectral_mask_table()
    dbm.populate_truth_parameters_table()

    seed(dbm.config["seed"])

    if logging:
        logger.debug(f"Seed: {dbm.config['seed']}")
        logger.debug("Configuration:")
        logger.debug(yaml.dump(dbm.config))

    dbm.populate_source_file_table(show_progress)
    dbm.populate_impulse_response_file_table(show_progress)

    mixtures = dbm.generate_mixtures()
    num_mixtures = len(mixtures)

    if logging:
        logger.info(f"Found {num_mixtures:,} mixtures to process")

    total_duration = float(sum([mixture.samples for mixture in mixtures])) / SAMPLE_RATE

    if logging:
        log_duration_and_sizes(
            total_duration=total_duration,
            feature_step_samples=mixdb.feature_step_samples,
            feature_parameters=mixdb.feature_parameters,
            stride=mixdb.fg_stride,
            desc="Estimated",
        )
        logger.info(
            f"Feature shape:        "
            f"{mixdb.fg_stride} x {mixdb.feature_parameters} "
            f"({mixdb.fg_stride * mixdb.feature_parameters} total parameters)"
        )
        logger.info(f"Feature samples:      {mixdb.feature_samples} samples ({mixdb.feature_ms} ms)")
        logger.info(f"Feature step samples: {mixdb.feature_step_samples} samples ({mixdb.feature_step_ms} ms)")
        logger.info("")

    # Fill in the details
    if logging:
        logger.info("Processing mixtures")
    progress = track(total=num_mixtures, disable=not show_progress)
    mixtures = par_track(
        partial(
            _process_mixture,
            location=location,
            save_mix=save_mix,
            test=test,
        ),
        mixtures,
        progress=progress,
        no_par=no_par,
        pass_index=True,
    )
    progress.close()

    dbm.populate_mixture_table(mixtures=mixtures, show_progress=show_progress)

    total_duration = float(mixdb.total_samples() / SAMPLE_RATE)

    if logging:
        log_duration_and_sizes(
            total_duration=total_duration,
            feature_step_samples=mixdb.feature_step_samples,
            feature_parameters=mixdb.feature_parameters,
            stride=mixdb.fg_stride,
            desc="Actual",
        )
        logger.info("")

    if not test and save_json:
        if logging:
            logger.info(f"Writing JSON version of database to {location}")
        mixdb = MixtureDatabase(location)
        mixdb.save()


def _process_mixture(
    index: int,
    mixture: Mixture,
    location: str,
    save_mix: bool,
    test: bool,
) -> Mixture:
    mixdb = MixtureDatabase(location, test=test)
    mixture.name = f"{index:0{mixdb.mixid_width}}"
    mixture, genmix_data = update_mixture(mixdb, mixture, save_mix)

    write = partial(write_cached_data, location=location, name="mixture", index=mixture.name)

    if save_mix:
        write(
            items={
                "sources": genmix_data.sources,
                "source": genmix_data.source,
                "noise": genmix_data.noise,
                "mixture": genmix_data.mixture,
            }
        )

        write_mixture_metadata(mixdb, mixture=mixture)

    return mixture


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils.docstring import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    import time
    from os import makedirs
    from os import remove
    from os.path import exists
    from os.path import isdir
    from os.path import join

    import yaml

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import logger
    from sonusai import update_console_handler
    from sonusai.config.config import load_config
    from sonusai.utils.seconds_to_hms import seconds_to_hms

    verbose = args["--verbose"]
    save_mix = args["--mix"]
    dryrun = args["--dryrun"]
    save_json = args["--json"]
    no_par = args["--nopar"]
    location = args["LOC"]

    start_time = time.monotonic()

    if exists(location) and not isdir(location):
        remove(location)

    makedirs(location, exist_ok=True)

    create_file_handler(join(location, "genmixdb.log"), verbose)
    update_console_handler(verbose)
    initial_log_messages("genmixdb")

    if dryrun:
        config = load_config(location)
        logger.info("Dryrun configuration:")
        logger.info(yaml.dump(config))
        return

    logger.info(f"Creating mixture database for {location}")
    logger.info("")

    genmixdb(
        location=location,
        save_mix=save_mix,
        show_progress=True,
        save_json=save_json,
        verbose=verbose,
        no_par=no_par,
    )

    end_time = time.monotonic()
    logger.info(f"Completed in {seconds_to_hms(seconds=end_time - start_time)}")
    logger.info("")


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils.keyboard_interrupt import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)
