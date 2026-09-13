"""Import the CC BY 4.0 NEU-DET YOLO dataset into the combined dataset."""

from __future__ import annotations

import argparse
import random
import shutil
from collections import Counter
from pathlib import Path


CLASS_MAP = {
    0: 5,   # crazing
    1: 6,   # inclusion
    2: 7,   # patches
    3: 8,   # pitted surface
    4: 9,   # rolled-in scale
    5: 0,   # scratches -> shared Surface Scratch class
}


def import_dataset(source: Path, destination: Path, val_fraction: float = 0.2, seed: int = 42) -> None:
    pairs: list[tuple[Path, Path]] = []
    for split in ("train", "val"):
        for image in sorted((source / "images" / split).glob("*")):
            if image.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            label = source / "labels" / split / f"{image.stem}.txt"
            if not label.exists():
                raise FileNotFoundError(f"Missing label for {image.name}")
            pairs.append((image, label))

    if not pairs:
        raise FileNotFoundError(f"No image/label pairs found below {source}")

    rng = random.Random(seed)
    rng.shuffle(pairs)
    validation = {image.resolve() for image, _ in pairs[: round(len(pairs) * val_fraction)]}
    counts: Counter[int] = Counter()

    for image, label in pairs:
        split = "val" if image.resolve() in validation else "train"
        target_stem = f"neu_{image.stem}"
        mapped: list[str] = []
        for row in label.read_text(encoding="utf-8").splitlines():
            fields = row.split()
            if len(fields) != 5:
                raise ValueError(f"Invalid YOLO annotation in {label}: {row!r}")
            source_id = int(fields[0])
            if source_id not in CLASS_MAP:
                raise ValueError(f"Unknown NEU-DET class {source_id} in {label}")
            target_id = CLASS_MAP[source_id]
            coordinates = [float(value) for value in fields[1:]]
            if not all(0 <= value <= 1 for value in coordinates) or coordinates[2] <= 0 or coordinates[3] <= 0:
                raise ValueError(f"Invalid bounding box in {label}: {row!r}")
            mapped.append(" ".join([str(target_id), *fields[1:]]))
            counts[target_id] += 1

        image_target = destination / "images" / split / f"{target_stem}{image.suffix.lower()}"
        label_target = destination / "labels" / split / f"{target_stem}.txt"
        image_target.parent.mkdir(parents=True, exist_ok=True)
        label_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, image_target)
        label_target.write_text("\n".join(mapped) + "\n", encoding="utf-8")

    print(f"Imported {len(pairs) - len(validation)} train and {len(validation)} validation images")
    print(f"Mapped annotations by target class: {dict(sorted(counts.items()))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--val-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    import_dataset(args.source, args.destination, args.val_fraction, args.seed)
