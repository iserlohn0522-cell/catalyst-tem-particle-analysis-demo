from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


FIELDNAMES = [
    "image_id",
    "split",
    "image_path",
    "label_path",
    "nm_per_px",
    "source",
    "allowed_use",
    "sha256_image",
]


@dataclass(frozen=True)
class ManifestRow:
    image_id: str
    split: str
    image_path: str
    label_path: str
    nm_per_px: float
    source: str
    allowed_use: str
    sha256_image: str

    def as_csv_row(self) -> dict[str, str]:
        return {
            "image_id": self.image_id,
            "split": self.split,
            "image_path": self.image_path,
            "label_path": self.label_path,
            "nm_per_px": f"{self.nm_per_px:.6f}",
            "source": self.source,
            "allowed_use": self.allowed_use,
            "sha256_image": self.sha256_image,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(path: Path, rows: Iterable[ManifestRow]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_csv_row())
    return path


def read_manifest(path: Path) -> list[ManifestRow]:
    path = Path(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        missing = [field for field in FIELDNAMES if field not in fieldnames]
        if missing:
            raise ValueError(f"Manifest is missing required columns: {missing}")
        rows = []
        for row in reader:
            rows.append(
                ManifestRow(
                    image_id=str(row["image_id"]),
                    split=str(row["split"]),
                    image_path=str(row["image_path"]),
                    label_path=str(row["label_path"]),
                    nm_per_px=float(row["nm_per_px"]),
                    source=str(row["source"]),
                    allowed_use=str(row["allowed_use"]),
                    sha256_image=str(row["sha256_image"]),
                )
            )
        return rows


def resolve_manifest_path(manifest_path: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError(f"Manifest path must be relative, got: {relative_path}")
    return (Path(manifest_path).parent / candidate).resolve()


def validate_manifest(path: Path) -> list[ManifestRow]:
    rows = read_manifest(path)
    seen_ids: set[str] = set()
    for row in rows:
        if row.image_id in seen_ids:
            raise ValueError(f"Duplicate image_id: {row.image_id}")
        seen_ids.add(row.image_id)
        if row.source != "synthetic_generated":
            raise ValueError(f"Unsafe source for {row.image_id}: {row.source}")
        if row.allowed_use != "public_demo_only":
            raise ValueError(f"Unexpected allowed_use for {row.image_id}: {row.allowed_use}")
        if row.nm_per_px <= 0:
            raise ValueError(f"nm_per_px must be positive for {row.image_id}")
        image_path = resolve_manifest_path(path, row.image_path)
        label_path = resolve_manifest_path(path, row.label_path)
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        if not label_path.exists():
            raise FileNotFoundError(label_path)
        actual = sha256_file(image_path)
        if actual != row.sha256_image:
            raise ValueError(f"sha256 mismatch for {row.image_id}: expected {row.sha256_image}, got {actual}")
    return rows
