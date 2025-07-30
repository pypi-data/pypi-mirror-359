# ruff: noqa: S608
import json
from functools import partial
from os.path import join
from pathlib import Path
from random import choice
from random import randint

import numpy as np
import pandas as pd
import yaml
from praatio import textgrid

from .. import logger
from ..config.config import load_config
from ..config.ir import get_ir_files
from ..config.source import get_source_files
from ..constants import SAMPLE_BYTES
from ..constants import SAMPLE_RATE
from ..datatypes import AudioT
from ..datatypes import Effects
from ..datatypes import GenMixData
from ..datatypes import ImpulseResponseFile
from ..datatypes import Mixture
from ..datatypes import Source
from ..datatypes import SourceFile
from ..datatypes import SourcesAudioT
from ..datatypes import UniversalSNRGenerator
from ..utils.human_readable_size import human_readable_size
from ..utils.seconds_to_hms import seconds_to_hms
from .db import SQLiteDatabase
from .effects import get_effect_rules
from .mixdb import MixtureDatabase


def config_file(location: str) -> str:
    return join(location, "config.yml")


# Database schema definition
DATABASE_SCHEMA = [
    """
    CREATE TABLE truth_config(
    id INTEGER PRIMARY KEY NOT NULL,
    config TEXT NOT NULL)
    """,
    """
    CREATE TABLE truth_parameters(
    id INTEGER PRIMARY KEY NOT NULL,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    parameters INTEGER)
    """,
    """
    CREATE TABLE source_file (
    id INTEGER PRIMARY KEY NOT NULL,
    category TEXT NOT NULL,
    class_indices TEXT,
    level_type TEXT NOT NULL,
    name TEXT NOT NULL,
    samples INTEGER NOT NULL,
    speaker_id INTEGER,
    FOREIGN KEY(speaker_id) REFERENCES speaker (id))
    """,
    """
    CREATE TABLE ir_file (
    id INTEGER PRIMARY KEY NOT NULL,
    delay INTEGER NOT NULL,
    name TEXT NOT NULL)
    """,
    """
    CREATE TABLE ir_tag (
    id INTEGER PRIMARY KEY NOT NULL,
    tag TEXT NOT NULL UNIQUE)
    """,
    """
    CREATE TABLE ir_file_ir_tag (
    file_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(file_id) REFERENCES ir_file (id),
    FOREIGN KEY(tag_id) REFERENCES ir_tag (id))
    """,
    """
    CREATE TABLE speaker (
    id INTEGER PRIMARY KEY NOT NULL,
    parent TEXT NOT NULL)
    """,
    """
    CREATE TABLE top (
    id INTEGER PRIMARY KEY NOT NULL,
    asr_configs TEXT NOT NULL,
    class_balancing BOOLEAN NOT NULL,
    feature TEXT NOT NULL,
    mixid_width INTEGER NOT NULL,
    num_classes INTEGER NOT NULL,
    seed INTEGER NOT NULL,
    speaker_metadata_tiers TEXT NOT NULL,
    textgrid_metadata_tiers TEXT NOT NULL,
    version INTEGER NOT NULL)
    """,
    """
    CREATE TABLE class_label (
    id INTEGER PRIMARY KEY NOT NULL,
    label TEXT NOT NULL)
    """,
    """
    CREATE TABLE class_weights_threshold (
    id INTEGER PRIMARY KEY NOT NULL,
    threshold FLOAT NOT NULL)
    """,
    """
    CREATE TABLE spectral_mask (
    id INTEGER PRIMARY KEY NOT NULL,
    f_max_width INTEGER NOT NULL,
    f_num INTEGER NOT NULL,
    t_max_percent INTEGER NOT NULL,
    t_max_width INTEGER NOT NULL,
    t_num INTEGER NOT NULL)
    """,
    """
    CREATE TABLE source_file_truth_config (
    source_file_id INTEGER NOT NULL,
    truth_config_id INTEGER NOT NULL,
    FOREIGN KEY(source_file_id) REFERENCES source_file (id),
    FOREIGN KEY(truth_config_id) REFERENCES truth_config (id))
    """,
    """
    CREATE TABLE source (
    id INTEGER PRIMARY KEY NOT NULL,
    effects TEXT NOT NULL,
    file_id INTEGER NOT NULL,
    pre_tempo FLOAT NOT NULL,
    repeat BOOLEAN NOT NULL,
    snr FLOAT NOT NULL,
    snr_gain FLOAT NOT NULL,
    snr_random BOOLEAN NOT NULL,
    start INTEGER NOT NULL,
    UNIQUE(effects, file_id, pre_tempo, repeat, snr, snr_gain, snr_random, start),
    FOREIGN KEY(file_id) REFERENCES source_file (id))
    """,
    """
    CREATE TABLE mixture (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    samples INTEGER NOT NULL,
    spectral_mask_id INTEGER NOT NULL,
    spectral_mask_seed INTEGER NOT NULL,
    FOREIGN KEY(spectral_mask_id) REFERENCES spectral_mask (id))
    """,
    """
    CREATE TABLE mixture_source (
    mixture_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    FOREIGN KEY(mixture_id) REFERENCES mixture (id),
    FOREIGN KEY(source_id) REFERENCES source (id))
    """,
]


class DatabaseManager:
    """Manages database operations for mixture database generation."""

    def __init__(self, location: str, test: bool = False, verbose: bool = False, logging: bool = False) -> None:
        self.location = location
        self.test = test
        self.verbose = verbose
        self.logging = logging

        self.config = load_config(self.location)
        self.db = partial(SQLiteDatabase, location=self.location, test=self.test, verbose=self.verbose)

        with self.db(create=True) as c:
            for table_sql in DATABASE_SCHEMA:
                c.execute(table_sql)

        self.mixdb = MixtureDatabase(location=self.location, test=self.test)

    def populate_top_table(self) -> None:
        """Populate the top table"""
        from .constants import MIXDB_VERSION

        parameters = (
            1,
            json.dumps(self.config["asr_configs"]),
            self.config["class_balancing"],
            self.config["feature"],
            0,
            self.config["num_classes"],
            self.config["seed"],
            "",
            "",
            MIXDB_VERSION,
        )

        with self.db(readonly=False) as c:
            c.execute(
                """
                INSERT INTO top (id, asr_configs, class_balancing, feature, mixid_width, num_classes,
                                 seed, speaker_metadata_tiers, textgrid_metadata_tiers, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                parameters,
            )

    def populate_class_label_table(self) -> None:
        """Populate the class_label table"""
        with self.db(readonly=False) as c:
            c.executemany(
                "INSERT INTO class_label (label) VALUES (?)",
                [(item,) for item in self.config["class_labels"]],
            )

    def populate_class_weights_threshold_table(self) -> None:
        """Populate the class_weights_threshold table"""
        class_weights_threshold = self.config["class_weights_threshold"]
        num_classes = self.config["num_classes"]

        if not isinstance(class_weights_threshold, list):
            class_weights_threshold = [class_weights_threshold]

        if len(class_weights_threshold) == 1:
            class_weights_threshold = [class_weights_threshold[0]] * num_classes

        if len(class_weights_threshold) != num_classes:
            raise ValueError(f"invalid class_weights_threshold length: {len(class_weights_threshold)}")

        with self.db(readonly=False) as c:
            c.executemany(
                "INSERT INTO class_weights_threshold (threshold) VALUES (?)",
                [(item,) for item in class_weights_threshold],
            )

    def populate_spectral_mask_table(self) -> None:
        """Populate the spectral_mask table"""
        from ..config.spectral_masks import get_spectral_masks

        with self.db(readonly=False) as c:
            c.executemany(
                """
            INSERT INTO spectral_mask (f_max_width, f_num, t_max_percent, t_max_width, t_num) VALUES (?, ?, ?, ?, ?)
            """,
                [
                    (
                        item.f_max_width,
                        item.f_num,
                        item.t_max_percent,
                        item.t_max_width,
                        item.t_num,
                    )
                    for item in get_spectral_masks(self.config)
                ],
            )

    def populate_truth_parameters_table(self) -> None:
        """Populate the truth_parameters table"""
        from ..config.truth import get_truth_parameters

        with self.db(readonly=False) as c:
            c.executemany(
                """
            INSERT INTO truth_parameters (category, name, parameters) VALUES (?, ?, ?)
            """,
                [
                    (
                        item.category,
                        item.name,
                        item.parameters,
                    )
                    for item in get_truth_parameters(self.config)
                ],
            )

    def populate_source_file_table(self, show_progress: bool = False) -> None:
        """Populate the source file table"""
        if self.logging:
            logger.info("Collecting sources")

        files = get_source_files(self.config, show_progress)
        logger.info("")

        if len([file for file in files if file.category == "primary"]) == 0:
            raise RuntimeError("Canceled due to no primary sources")

        if self.logging:
            logger.info("Populating source file table")

        self._populate_truth_config_table(files)
        self._populate_speaker_table(files)

        with self.db(readonly=False) as c:
            textgrid_metadata_tiers: set[str] = set()
            for file in files:
                # Get TextGrid tiers for the source file and add to the collection
                tiers = _get_textgrid_tiers_from_source_file(file.name)
                for tier in tiers:
                    textgrid_metadata_tiers.add(tier)

                # Get truth settings for the file
                truth_config_ids: list[int] = []
                if file.truth_configs:
                    for name, config in file.truth_configs.items():
                        ts = json.dumps({"name": name} | config.to_dict())
                        c.execute(
                            "SELECT truth_config.id FROM truth_config WHERE ? = truth_config.config",
                            (ts,),
                        )
                        truth_config_ids.append(c.fetchone()[0])

                # Get speaker_id for the source file
                c.execute(
                    "SELECT speaker.id FROM speaker WHERE ? = speaker.parent", (Path(file.name).parent.as_posix(),)
                )
                result = c.fetchone()
                speaker_id = None
                if result is not None:
                    speaker_id = result[0]

                # Add entry
                c.execute(
                    """
                    INSERT INTO source_file (category, class_indices, level_type, name, samples, speaker_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        file.category,
                        json.dumps(file.class_indices),
                        file.level_type,
                        file.name,
                        file.samples,
                        speaker_id,
                    ),
                )
                source_file_id = c.lastrowid
                for truth_config_id in truth_config_ids:
                    c.execute(
                        "INSERT INTO source_file_truth_config (source_file_id, truth_config_id) VALUES (?, ?)",
                        (source_file_id, truth_config_id),
                    )

            # Update textgrid_metadata_tiers in the top table
            c.execute(
                "UPDATE top SET textgrid_metadata_tiers=? WHERE ? = id",
                (json.dumps(sorted(textgrid_metadata_tiers)), 1),
            )

        if self.logging:
            logger.info("Sources summary")
            data = {
                "category": [],
                "files": [],
                "size": [],
                "duration": [],
            }
            for category, files in self.mixdb.source_files.items():
                audio_samples = sum([source.samples for source in files])
                audio_duration = audio_samples / SAMPLE_RATE
                data["category"].append(category)
                data["files"].append(self.mixdb.num_source_files(category))
                data["size"].append(human_readable_size(audio_samples * SAMPLE_BYTES, 1))
                data["duration"].append(seconds_to_hms(seconds=audio_duration))

            df = pd.DataFrame(data)
            logger.info(df.to_string(index=False, header=False))
            logger.info("")

            for category, files in self.mixdb.source_files.items():
                logger.debug(f"List of {category} sources:")
                logger.debug(yaml.dump([file.name for file in files], default_flow_style=False))

    def populate_impulse_response_file_table(self, show_progress: bool = False) -> None:
        """Populate the impulse response file table"""
        if self.logging:
            logger.info("Collecting impulse responses")

        files = get_ir_files(self.config, show_progress=show_progress)
        logger.info("")

        if self.logging:
            logger.info("Populating impulse response file table")

        self._populate_impulse_response_tag_table(files)

        with self.db(readonly=False) as c:
            for file in files:
                # Get the tags for the file
                tag_ids: list[int] = []
                for tag in file.tags:
                    c.execute("SELECT id FROM ir_tag WHERE ? = tag", (tag,))
                    tag_ids.append(c.fetchone()[0])

                c.execute("INSERT INTO ir_file (delay, name) VALUES (?, ?)", (file.delay, file.name))

                file_id = c.lastrowid
                for tag_id in tag_ids:
                    c.execute("INSERT INTO ir_file_ir_tag (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))

        if self.logging:
            logger.debug("List of impulse responses:")
            for idx, file in enumerate(files):
                logger.debug(f"id: {idx}, name:{file.name}, delay: {file.delay}, tags: [{', '.join(file.tags)}]")
            logger.debug("")

    def populate_mixture_table(self, mixtures: list[Mixture], show_progress: bool = False) -> None:
        """Populate the mixture table"""
        from ..utils.parallel import track
        from .helpers import from_mixture
        from .helpers import from_source

        if self.logging:
            logger.info("Populating mixture and source tables")

        with self.db(readonly=False) as c:
            # Populate the source table
            for mixture in track(mixtures, disable=not show_progress):
                m_id = int(mixture.name) + 1
                c.execute(
                    """
                    INSERT INTO mixture (id, name, samples, spectral_mask_id, spectral_mask_seed)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (m_id, *from_mixture(mixture)),
                )

                for source in mixture.all_sources.values():
                    c.execute(
                        """
                    INSERT OR IGNORE INTO source (effects, file_id, pre_tempo, repeat, snr, snr_gain, snr_random, start)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        from_source(source),
                    )

                    source_id = c.execute(
                        """
                        SELECT id
                        FROM source
                        WHERE ? = effects
                        AND ? = file_id
                        AND ? = pre_tempo
                        AND ? = repeat
                        AND ? = snr
                        AND ? = snr_gain
                        AND ? = snr_random
                        AND ? = start
                    """,
                        from_source(source),
                    ).fetchone()[0]
                    c.execute("INSERT INTO mixture_source (mixture_id, source_id) VALUES (?, ?)", (m_id, source_id))

            if self.logging:
                logger.info("Closing mixture and source tables")

    def _populate_speaker_table(self, source_files: list[SourceFile]) -> None:
        """Populate the speaker table"""
        from ..utils.tokenized_shell_vars import tokenized_expand

        # Determine the columns for speaker the table
        all_parents = {Path(file.name).parent for file in source_files}
        speaker_parents = (
            parent for parent in all_parents if Path(tokenized_expand(parent / "speaker.yml")[0]).exists()
        )

        speakers: dict[Path, dict[str, str]] = {}
        for parent in sorted(speaker_parents):
            with open(tokenized_expand(parent / "speaker.yml")[0]) as f:
                speakers[parent] = yaml.safe_load(f)

        new_columns: list[str] = []
        for keys in speakers:
            for column in speakers[keys]:
                new_columns.append(column)
        new_columns = sorted(set(new_columns))

        with self.db(readonly=False) as c:
            for new_column in new_columns:
                c.execute(f"ALTER TABLE speaker ADD COLUMN {new_column} TEXT")

            # Populate the speaker table
            speaker_rows: list[tuple[str, ...]] = []
            for key in speakers:
                entry = (speakers[key].get(column, None) for column in new_columns)
                speaker_rows.append((key.as_posix(), *entry))  # type: ignore[arg-type]

            column_ids = ", ".join(["parent", *new_columns])
            column_values = ", ".join(["?"] * (len(new_columns) + 1))
            c.executemany(f"INSERT INTO speaker ({column_ids}) VALUES ({column_values})", speaker_rows)

            c.execute("CREATE INDEX speaker_parent_idx ON speaker (parent)")

            # Update speaker_metadata_tiers in the top table
            tiers = [
                description[0]
                for description in c.execute("SELECT * FROM speaker").description
                if description[0] not in ("id", "parent")
            ]
            c.execute("UPDATE top SET speaker_metadata_tiers=? WHERE ? = id", (json.dumps(tiers), 1))

            if "speaker_id" in tiers:
                c.execute("CREATE INDEX speaker_speaker_id_idx ON source_file (speaker_id)")

    def _populate_truth_config_table(self, source_files: list[SourceFile]) -> None:
        """Populate the truth_config table"""
        with self.db(readonly=False) as c:
            # Populate truth_config table
            truth_configs: list[str] = []
            for file in source_files:
                for name, config in file.truth_configs.items():
                    ts = json.dumps({"name": name} | config.to_dict())
                    if ts not in truth_configs:
                        truth_configs.append(ts)
            c.executemany(
                "INSERT INTO truth_config (config) VALUES (?)",
                [(item,) for item in truth_configs],
            )

    def _populate_impulse_response_tag_table(self, files: list[ImpulseResponseFile]) -> None:
        """Populate the ir_tag table"""
        with self.db(readonly=False) as c:
            c.executemany(
                "INSERT INTO ir_tag (tag) VALUES (?)",
                [(tag,) for tag in {tag for file in files for tag in file.tags}],
            )

    def generate_mixtures(self) -> list[Mixture]:
        """Generate mixtures"""
        from ..utils.max_text_width import max_text_width

        if self.logging:
            logger.info("Collecting effects")

        rules = get_effect_rules(self.location, self.config, self.test)

        if self.logging:
            logger.info("")
            for category, effect in rules.items():
                logger.debug(f"List of {category} rules:")
                logger.debug(yaml.dump([entry.to_dict() for entry in effect], default_flow_style=False))

        if self.logging:
            logger.debug("SNRS:")
            for category, source in self.config["sources"].items():
                if category != "primary":
                    logger.debug(f"  {category}")
                    for snr in source["snrs"]:
                        logger.debug(f"  - {snr}")
            logger.debug("")
            logger.debug("Mix Rules:")
            for category, source in self.config["sources"].items():
                if category != "primary":
                    logger.debug(f"  {category}")
                    for mix_rule in source["mix_rules"]:
                        logger.debug(f"  - {mix_rule}")
            logger.debug("")
            logger.debug("Spectral masks:")
            for spectral_mask in self.mixdb.spectral_masks:
                logger.debug(f"- {spectral_mask}")
            logger.debug("")

        if self.logging:
            logger.info("Generating mixtures")

        effected_sources: dict[str, list[tuple[SourceFile, Effects]]] = {}
        for category in self.mixdb.source_files:
            effected_sources[category] = []
            for file in self.mixdb.source_files[category]:
                for rule in rules[category]:
                    effected_sources[category].append((file, rule))

        # First, create mixtures of primary and noise
        mixtures: list[Mixture] = []
        for mix_rule in self.config["sources"]["noise"]["mix_rules"]:
            mixtures.extend(
                self._process_noise_sources(
                    primary_effected_sources=effected_sources["primary"],
                    noise_effected_sources=effected_sources["noise"],
                    mix_rule=mix_rule,
                )
            )

        # Next, cycle through any additional sources and apply mix rules for each
        additional_sources = [cat for cat in self.mixdb.source_files if cat not in ("primary", "noise")]
        for category in additional_sources:
            new_mixtures: list[Mixture] = []
            for mix_rule in self.config["sources"][category]["mix_rules"]:
                new_mixtures.extend(
                    self._process_additional_sources(
                        effected_sources=effected_sources[category],
                        mixtures=mixtures,
                        category=category,
                        mix_rule=mix_rule,
                    )
                )
            mixtures = new_mixtures

        # Update the mixid width
        with self.db(readonly=False) as c:
            c.execute("UPDATE top SET mixid_width=? WHERE ? = id", (max_text_width(len(mixtures)), 1))

        return mixtures

    def _process_noise_sources(
        self,
        primary_effected_sources: list[tuple[SourceFile, Effects]],
        noise_effected_sources: list[tuple[SourceFile, Effects]],
        mix_rule: str,
    ) -> list[Mixture]:
        match mix_rule:
            case "exhaustive":
                return self._noise_exhaustive(primary_effected_sources, noise_effected_sources)
            case "non-exhaustive":
                return self._noise_non_exhaustive(primary_effected_sources, noise_effected_sources)
            case "non-combinatorial":
                return self._noise_non_combinatorial(primary_effected_sources, noise_effected_sources)
            case _:
                raise ValueError(f"invalid noise mix_rule: {mix_rule}")

    def _noise_exhaustive(
        self,
        primary_effected_sources: list[tuple[SourceFile, Effects]],
        noise_effected_sources: list[tuple[SourceFile, Effects]],
    ) -> list[Mixture]:
        """Use every noise/effect with every source/effect+interferences/effect"""
        from ..datatypes import Mixture
        from ..datatypes import UniversalSNR
        from .effects import effects_from_rules
        from .effects import estimate_effected_length

        snrs = self.all_snrs()

        mixtures: list[Mixture] = []
        for noise_file, noise_rule in noise_effected_sources:
            noise_start = 0
            noise_effect = effects_from_rules(self.mixdb, noise_rule)
            noise_length = estimate_effected_length(noise_file.samples, noise_effect)

            for primary_file, primary_rule in primary_effected_sources:
                primary_effect = effects_from_rules(self.mixdb, primary_rule)
                primary_length = estimate_effected_length(
                    primary_file.samples, primary_effect, self.mixdb.feature_step_samples
                )

                for spectral_mask_id in range(len(self.config["spectral_masks"])):
                    for snr in snrs["noise"]:
                        mixtures.append(
                            Mixture(
                                name="",
                                all_sources={
                                    "primary": Source(
                                        file_id=primary_file.id,
                                        effects=primary_effect,
                                    ),
                                    "noise": Source(
                                        file_id=noise_file.id,
                                        effects=noise_effect,
                                        start=noise_start,
                                        loop=True,
                                        snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                                    ),
                                },
                                samples=primary_length,
                                spectral_mask_id=spectral_mask_id + 1,
                                spectral_mask_seed=randint(0, np.iinfo("i").max),  # noqa: S311
                            )
                        )
                        noise_start = int((noise_start + primary_length) % noise_length)

        return mixtures

    def _noise_non_exhaustive(
        self,
        primary_effected_sources: list[tuple[SourceFile, Effects]],
        noise_effected_sources: list[tuple[SourceFile, Effects]],
    ) -> list[Mixture]:
        """Cycle through every source/effect+interferences/effect without necessarily using all
        noise/effect combinations (reduced data set).
        """
        from ..datatypes import Mixture
        from ..datatypes import UniversalSNR
        from .effects import effects_from_rules
        from .effects import estimate_effected_length

        snrs = self.all_snrs()

        next_noise = NextNoise(self.mixdb, noise_effected_sources)

        mixtures: list[Mixture] = []
        for primary_file, primary_rule in primary_effected_sources:
            primary_effect = effects_from_rules(self.mixdb, primary_rule)
            primary_length = estimate_effected_length(
                primary_file.samples, primary_effect, self.mixdb.feature_step_samples
            )

            for spectral_mask_id in range(len(self.config["spectral_masks"])):
                for snr in snrs["noise"]:
                    noise_file_id, noise_effect, noise_start = next_noise.generate(primary_file.samples)

                    mixtures.append(
                        Mixture(
                            name="",
                            all_sources={
                                "primary": Source(
                                    file_id=primary_file.id,
                                    effects=primary_effect,
                                ),
                                "noise": Source(
                                    file_id=noise_file_id,
                                    effects=noise_effect,
                                    start=noise_start,
                                    loop=True,
                                    snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                                ),
                            },
                            samples=primary_length,
                            spectral_mask_id=spectral_mask_id + 1,
                            spectral_mask_seed=randint(0, np.iinfo("i").max),  # noqa: S311
                        )
                    )

        return mixtures

    def _noise_non_combinatorial(
        self,
        primary_effected_sources: list[tuple[SourceFile, Effects]],
        noise_effected_sources: list[tuple[SourceFile, Effects]],
    ) -> list[Mixture]:
        """Combine a source/effect+interferences/effect with a single cut of a noise/effect
        non-exhaustively (each source/effect+interferences/effect does not use each noise/effect).
        Cut has a random start and loop back to the beginning if the end of noise/effect is reached.
        """
        from ..datatypes import Mixture
        from ..datatypes import UniversalSNR
        from .effects import effects_from_rules
        from .effects import estimate_effected_length

        snrs = self.all_snrs()

        noise_id = 0
        mixtures: list[Mixture] = []
        for primary_file, primary_rule in primary_effected_sources:
            primary_effect = effects_from_rules(self.mixdb, primary_rule)
            primary_length = estimate_effected_length(
                primary_file.samples, primary_effect, self.mixdb.feature_step_samples
            )

            for spectral_mask_id in range(len(self.config["spectral_masks"])):
                for snr in snrs["noise"]:
                    noise_file, noise_rule = noise_effected_sources[noise_id]
                    noise_effect = effects_from_rules(self.mixdb, noise_rule)
                    noise_length = estimate_effected_length(noise_file.samples, noise_effect)

                    mixtures.append(
                        Mixture(
                            name="",
                            all_sources={
                                "primary": Source(
                                    file_id=primary_file.id,
                                    effects=primary_effect,
                                ),
                                "noise": Source(
                                    file_id=noise_file.id,
                                    effects=noise_effect,
                                    start=choice(range(noise_length)),  # noqa: S311
                                    loop=True,
                                    snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                                ),
                            },
                            samples=primary_length,
                            spectral_mask_id=spectral_mask_id + 1,
                            spectral_mask_seed=randint(0, np.iinfo("i").max),  # noqa: S311
                        )
                    )
                    noise_id = (noise_id + 1) % len(noise_effected_sources)

        return mixtures

    def _process_additional_sources(
        self,
        effected_sources: list[tuple[SourceFile, Effects]],
        mixtures: list[Mixture],
        category: str,
        mix_rule: str,
    ) -> list[Mixture]:
        if mix_rule == "none":
            return mixtures
        if mix_rule.startswith("choose"):
            return self._additional_choose(
                effected_sources=effected_sources,
                mixtures=mixtures,
                category=category,
                mix_rule=mix_rule,
            )
        if mix_rule.startswith("sequence"):
            return self._additional_sequence(
                effected_sources=effected_sources,
                mixtures=mixtures,
                category=category,
                mix_rule=mix_rule,
            )
        raise ValueError(f"invalid {category} mix_rule: {mix_rule}")

    def _additional_choose(
        self,
        effected_sources: list[tuple[SourceFile, Effects]],
        mixtures: list[Mixture],
        category: str,
        mix_rule: str,
    ) -> list[Mixture]:
        from copy import deepcopy

        from ..datatypes import UniversalSNR
        from ..parse.parse_source_directive import parse_source_directive
        from ..utils.choice import RandomChoice

        # Parse the mix rule
        try:
            params = parse_source_directive(mix_rule)
        except ValueError as e:
            raise ValueError(f"Error parsing choose directive: {e}") from e

        snrs = self.all_snrs()[category]

        choice_objs: dict[tuple[int, ...], RandomChoice] = {}
        if params.unique == "speaker_id" :
            # Get a set of speaker_id values in use in the existing mixtures.
            all_speaker_ids = {self.get_mixture_speaker_ids(mixture) for mixture in mixtures}

            # Create a set of RandomChoice objects that are filtered on those values.
            for speaker_ids in all_speaker_ids:
                filtered_sources = _filter_sources(effected_sources, speaker_ids)
                if not filtered_sources:
                    raise ValueError(
                        f"Additional source, {category}, has no valid entries for speaker_ids unique from {speaker_ids}"
                    )
                choice_objs[speaker_ids] = RandomChoice(data=filtered_sources, repetition=params.repeat)
        elif params.unique is None:
            choice_objs = {(0,): RandomChoice(data=effected_sources, repetition=params.repeat)}
        else:
            raise ValueError(f"Invalid unique value: {params.unique}")

        # Loop over mixtures and add additional sources
        new_mixtures: list[Mixture] = []
        for mixture in mixtures:
            for snr in snrs:
                new_mixture = deepcopy(mixture)
                if params.unique == "speaker_id" :
                    speaker_ids = self.get_mixture_speaker_ids(mixture)
                elif params.unique is None:
                    speaker_ids = (0,)
                else:
                    raise ValueError(f"Invalid unique value: {params.unique}")
                source, effect = choice_objs[speaker_ids].next()
                new_source = Source(
                    file_id=source.id,
                    effects=effect,
                    start=params.start,
                    loop=params.loop,
                    snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                )
                new_mixture.all_sources[category] = new_source
                new_mixtures.append(new_mixture)

        return new_mixtures

    def _additional_sequence(
        self,
        effected_sources: list[tuple[SourceFile, Effects]],
        mixtures: list[Mixture],
        category: str,
        mix_rule: str,
    ) -> list[Mixture]:
        from copy import deepcopy

        from ..datatypes import UniversalSNR
        from ..parse.parse_source_directive import parse_source_directive
        from ..utils.choice import SequentialChoice

        # Parse the mix rule
        try:
            params = parse_source_directive(mix_rule)
        except ValueError as e:
            raise ValueError(f"Error parsing choose directive: {e}") from e

        snrs = self.all_snrs()[category]

        sequence_objs: dict[tuple[int, ...], SequentialChoice] = {}
        if params.unique == "speaker_id" :
            # Get a set of speaker_id values in use in the existing mixtures.
            all_speaker_ids = {self.get_mixture_speaker_ids(mixture) for mixture in mixtures}

            # Create a set of SequentialChoice objects that are filtered on those values.
            for speaker_ids in all_speaker_ids:
                filtered_sources = _filter_sources(effected_sources, speaker_ids)
                if not filtered_sources:
                    raise ValueError(
                        f"Additional source, {category}, has no valid entries for speaker_ids unique from {speaker_ids}"
                    )
                sequence_objs[speaker_ids] = SequentialChoice(data=filtered_sources)
        elif params.unique is None:
            sequence_objs = {(0,): SequentialChoice(data=effected_sources)}
        else:
            raise ValueError(f"Invalid unique value: {params.unique}")

        # Loop over mixtures and add additional sources
        new_mixtures: list[Mixture] = []
        for mixture in mixtures:
            for snr in snrs:
                new_mixture = deepcopy(mixture)
                if params.unique == "speaker_id" :
                    speaker_ids = self.get_mixture_speaker_ids(mixture)
                elif params.unique is None:
                    speaker_ids = (0,)
                else:
                    raise ValueError(f"Invalid unique value: {params.unique}")
                source, effect = sequence_objs[speaker_ids].next()
                new_source = Source(
                    file_id=source.id,
                    effects=effect,
                    start=params.start,
                    loop=params.loop,
                    snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                )
                new_mixture.all_sources[category] = new_source
                new_mixtures.append(new_mixture)

        return new_mixtures

    def get_mixture_speaker_ids(self, mixture: Mixture) -> tuple[int, ...]:
        """Get the speaker IDs used in a mixture, excluding None values"""
        valid_speaker_ids = [
            speaker_id
            for source in mixture.all_sources.values()
            if (speaker_id := self.mixdb.source_file(source.file_id).speaker_id) is not None
        ]
        return tuple(valid_speaker_ids)

    def all_snrs(self) -> dict[str, list[UniversalSNRGenerator]]:
        snrs: dict[str, list[UniversalSNRGenerator]] = {}
        for category in self.config["sources"]:
            if category != "primary":
                snrs[category] = [UniversalSNRGenerator(snr) for snr in self.config["sources"][category]["snrs"]]
        return snrs


def update_mixture(mixdb: MixtureDatabase, mixture: Mixture, with_data: bool = False) -> tuple[Mixture, GenMixData]:
    """Update mixture record with name, samples, and gains"""
    sources_audio: SourcesAudioT = {}
    post_audio: SourcesAudioT = {}
    for category in mixture.all_sources:
        mixture, sources_audio[category], post_audio[category] = _update_source(mixdb, mixture, category)

    mixture = _initialize_mixture_gains(mixdb, mixture, post_audio)

    if not with_data:
        return mixture, GenMixData()

    # Apply gains
    post_audio = {
        category: post_audio[category] * mixture.all_sources[category].snr_gain for category in mixture.all_sources
    }

    # Sum sources, noise, and mixture
    source_audio = np.sum([post_audio[category] for category in mixture.sources], axis=0)
    noise_audio = post_audio["noise"]
    mixture_audio = source_audio + noise_audio

    return mixture, GenMixData(
        sources=sources_audio,
        source=source_audio,
        noise=noise_audio,
        mixture=mixture_audio,
    )


def _update_source(mixdb: MixtureDatabase, mixture: Mixture, category: str) -> tuple[Mixture, AudioT, AudioT]:
    from .effects import apply_effects
    from .effects import conform_audio_to_length

    source = mixture.all_sources[category]
    org_audio = mixdb.read_source_audio(source.file_id)

    org_samples = len(org_audio)
    pre_audio = apply_effects(mixdb, org_audio, source.effects, pre=True, post=False)

    pre_samples = len(pre_audio)
    mixture.all_sources[category].pre_tempo = org_samples / pre_samples

    pre_audio = conform_audio_to_length(pre_audio, mixture.samples, source.loop, source.start)

    post_audio = apply_effects(mixdb, pre_audio, source.effects, pre=False, post=True)
    if len(pre_audio) != len(post_audio):
        raise RuntimeError(f"post-truth effects changed length: {source.effects.post}")

    return mixture, pre_audio, post_audio


def _initialize_mixture_gains(mixdb: MixtureDatabase, mixture: Mixture, sources_audio: SourcesAudioT) -> Mixture:
    from ..utils.asl_p56 import asl_p56
    from ..utils.db import db_to_linear

    sources_energy: dict[str, float] = {}
    for category in mixture.all_sources:
        level_type = mixdb.source_file(mixture.all_sources[category].file_id).level_type
        match level_type:
            case "default":
                sources_energy[category] = float(np.mean(np.square(sources_audio[category])))
            case "speech":
                sources_energy[category] = asl_p56(sources_audio[category])
            case _:
                raise ValueError(f"Unknown level_type: {level_type}")

    # Initialize all gains to 1
    for category in mixture.all_sources:
        mixture.all_sources[category].snr_gain = 1

    # Resolve gains
    for category in mixture.all_sources:
        if mixture.is_noise_only and category != "noise":
            # Special case for zeroing out source data
            mixture.all_sources[category].snr_gain = 0
        elif mixture.is_source_only and category == "noise":
            # Special case for zeroing out noise data
            mixture.all_sources[category].snr_gain = 0
        elif category != "primary":
            if sources_energy["primary"] == 0 or sources_energy[category] == 0:
                # Avoid divide-by-zero
                mixture.all_sources[category].snr_gain = 1
            else:
                mixture.all_sources[category].snr_gain = float(
                    np.sqrt(sources_energy["primary"] / sources_energy[category])
                ) / db_to_linear(mixture.all_sources[category].snr)

    # Normalize gains
    max_snr_gain = max([source.snr_gain for source in mixture.all_sources.values()])
    for category in mixture.all_sources:
        mixture.all_sources[category].snr_gain = mixture.all_sources[category].snr_gain / max_snr_gain

    # Check for clipping in mixture
    mixture_audio = np.sum(
        [sources_audio[category] * mixture.all_sources[category].snr_gain for category in mixture.all_sources], axis=0
    )
    max_abs_audio = float(np.max(np.abs(mixture_audio)))
    clip_level = db_to_linear(-0.25)
    if max_abs_audio > clip_level:
        gain_adjustment = clip_level / max_abs_audio
        for category in mixture.all_sources:
            mixture.all_sources[category].snr_gain *= gain_adjustment

    # To improve repeatability, round results
    for category in mixture.all_sources:
        mixture.all_sources[category].snr_gain = round(mixture.all_sources[category].snr_gain, ndigits=5)

    return mixture


class NextNoise:
    def __init__(self, mixdb: MixtureDatabase, effected_noises: list[tuple[SourceFile, Effects]]) -> None:
        from .effects import effects_from_rules
        from .effects import estimate_effected_length

        self.mixdb = mixdb
        self.effected_noises = effected_noises

        self.noise_start = 0
        self.noise_id = 0
        self.noise_effect = effects_from_rules(self.mixdb, self.noise_rule)
        self.noise_length = estimate_effected_length(self.noise_file.samples, self.noise_effect)

    @property
    def noise_file(self):
        return self.effected_noises[self.noise_id][0]

    @property
    def noise_rule(self):
        return self.effected_noises[self.noise_id][1]

    def generate(self, length: int) -> tuple[int, Effects, int]:
        from .effects import effects_from_rules
        from .effects import estimate_effected_length

        if self.noise_start + length > self.noise_length:
            # Not enough samples in current noise
            if self.noise_start == 0:
                raise ValueError("Length of primary audio exceeds length of noise audio")

            self.noise_start = 0
            self.noise_id = (self.noise_id + 1) % len(self.effected_noises)
            self.noise_effect = effects_from_rules(self.mixdb, self.noise_rule)
            self.noise_length = estimate_effected_length(self.noise_file.samples, self.noise_effect)
            noise_start = self.noise_start
        else:
            # Current noise has enough samples
            noise_start = self.noise_start
            self.noise_start += length

        return self.noise_file.id, self.noise_effect, noise_start


def _get_textgrid_tiers_from_source_file(file: str) -> list[str]:
    from ..utils.tokenized_shell_vars import tokenized_expand

    textgrid_file = Path(tokenized_expand(file)[0]).with_suffix(".TextGrid")
    if not textgrid_file.exists():
        return []

    tg = textgrid.openTextgrid(str(textgrid_file), includeEmptyIntervals=False)

    return sorted(tg.tierNames)


def _filter_sources(
    effected_sources: list[tuple[SourceFile, Effects]],
    speaker_id: tuple[int, ...],
) -> list[tuple[SourceFile, Effects]]:
    return [
        (source_file, effects) for source_file, effects in effected_sources if source_file.speaker_id not in speaker_id
    ]
