from __future__ import annotations

import json
from pathlib import Path

from tem_particle_demo.manifest import read_manifest, validate_manifest
from tem_particle_demo.synthetic import generate_dataset


def test_generate_dataset_writes_safe_manifest_and_labels(tmp_path: Path) -> None:
    manifest = generate_dataset(tmp_path / "synthetic", count=3, seed=11, size=96)

    rows = validate_manifest(manifest)

    assert len(rows) == 3
    assert all(row.source == "synthetic_generated" for row in rows)
    assert all(row.allowed_use == "public_demo_only" for row in rows)
    assert all(not Path(row.image_path).is_absolute() for row in rows)
    assert all(not Path(row.label_path).is_absolute() for row in rows)

    first_label = json.loads((manifest.parent / rows[0].label_path).read_text(encoding="utf-8"))
    assert first_label["description"] == "Synthetic TEM-like image generated for public demo use only."
    assert first_label["particles"]


def test_generate_dataset_is_reproducible(tmp_path: Path) -> None:
    manifest_a = generate_dataset(tmp_path / "a", count=2, seed=5, size=80)
    manifest_b = generate_dataset(tmp_path / "b", count=2, seed=5, size=80)

    rows_a = read_manifest(manifest_a)
    rows_b = read_manifest(manifest_b)

    assert [row.sha256_image for row in rows_a] == [row.sha256_image for row in rows_b]
