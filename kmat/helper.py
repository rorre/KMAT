import binascii
import os
import random
import tempfile
import time
import zipfile
from typing import IO, List, Union

from flask import current_app

import slider
from slider.beatmap import Beatmap, GameMode

from kmat.constants import ADJECTIVES, ANIMALS

StrPath = Union[str, os.PathLike]


def generate_id() -> str:
    timestamp = "{:x}".format(int(time.time()))
    rest = binascii.b2a_hex(os.urandom(8)).decode("ascii")
    return timestamp + rest


def generate_name() -> str:
    a = random.choice(ADJECTIVES)
    b = random.choice(ANIMALS)
    return f"{a} {b}"

def is_valid_metadata(bmap: slider.Beatmap):
    valid_metadata = current_app["metadata"]
    return (
        bmap.title == valid_metadata["title"] and
        bmap.artist == valid_metadata["artist"] and
        bmap.title_unicode == valid_metadata["title_unicode"] and
        bmap.artist_unicode == valid_metadata["artist_unicode"]
    )


def prepare_osz(file: IO[bytes], target_zip: StrPath, mapper_name: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(file, "r") as z:
            z.extractall(temp_dir)

        # Filter all files to look for .osu-s.
        diffs = list(filter(lambda x: x.endswith(".osu"), os.listdir(temp_dir)))
        if not diffs:
            raise ValueError("No difficulties found!")

        # Find highest diff in mapset
        # [Diffname, SR, Path, Beatmap]
        highest_diff: List[Union[str, int, Beatmap]] = ["", -1, "", None]
        for diff in diffs:
            diff_path = os.path.join(temp_dir, diff)
            with open(diff_path, encoding="utf8") as f:
                bmap = slider.Beatmap.from_file(f)

            if bmap.mode != GameMode.standard:
                continue

            sr = bmap.stars()
            if sr > highest_diff[1]:
                highest_diff = [bmap.version, sr, diff, bmap]

        if not highest_diff[-1]:
            raise ValueError("No osu!standard difficulty found.")
        
        if is_valid_metadata(highest_diff[-1]):
            return ValueError("Metadata is not valid.")

        # Diffname rule.
        valid_diffnames = ["easy", "normal", "hard", "insane", "expert", "extra"]
        if highest_diff[0].lower() not in valid_diffnames:
            raise ValueError(
                f'Invalid diffname "{highest_diff[0]}". Valid names are {valid_diffnames} (Case-insensitive)'
            )

        # Remove all diffs EXCEPT the highest one
        diffs.remove(highest_diff[2])
        for diff in diffs:
            diff_path = os.path.join(temp_dir, diff)
            os.remove(diff_path)

        # Replace mapper name
        original_path = os.path.join(temp_dir, highest_diff[2])
        new_path = os.path.join(temp_dir, f"{mapper_name}.osu")

        # An inefficient way to replace mapper name, really.
        fin = open(original_path, "rt")
        fout = open(new_path, "wt")
        for line in fin:
            fout.write(line.replace(highest_diff[-1].creator, mapper_name))
        fin.close()
        fout.close()

        # Remove diff before rename
        os.remove(original_path)

        # Save new osz
        with zipfile.ZipFile(target_zip, "w") as new_zip:
            with os.scandir(temp_dir) as it:
                for f in it:
                    if f.is_dir():
                        continue
                    new_zip.write(f.path, arcname=f.name)

    bmap: Beatmap = highest_diff[-1]
    return bmap.artist, bmap.title, bmap.version
