from __future__ import annotations

import json
from pathlib import Path

from tem_particle_demo.pipeline import run_pipeline
from tem_particle_demo.synthetic import generate_dataset


def test_pipeline_writes_report_summary_and_overlays(tmp_path: Path) -> None:
    manifest = generate_dataset(tmp_path / "dataset", count=2, seed=17, size=128)
    output = tmp_path / "outputs"

    report = run_pipeline(manifest, output, match_iou=0.25)

    assert report["demo_policy"]["data"] == "synthetic_generated_only"
    assert report["aggregate"]["image_count"] == 2
    assert report["aggregate"]["gt_count"] > 0
    assert (output / "report.json").exists()
    assert (output / "summary.md").exists()
    payload = json.loads((output / "report.json").read_text(encoding="utf-8"))
    for image_row in payload["images"]:
        assert (output / image_row["overlay_path"]).exists()
