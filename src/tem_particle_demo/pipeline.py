from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .detector import Box, detect_particles, load_grayscale
from .manifest import ManifestRow, read_manifest, resolve_manifest_path, validate_manifest
from .metrics import (
    match_detections,
    mask_stats,
    nearest_neighbor_distances_nm,
    precision_recall_f1,
    summarize_values,
)
from .overlays import save_overlay
from .segmentation import segment_detections


def _load_gt_boxes(label_path: Path) -> list[Box]:
    payload = json.loads(Path(label_path).read_text(encoding="utf-8"))
    boxes: list[Box] = []
    for particle in payload.get("particles", []):
        raw = particle.get("bbox", [])
        if len(raw) == 4:
            boxes.append((float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3])))
    return boxes


def _analyze_row(manifest_path: Path, row: ManifestRow, output_dir: Path, match_iou: float) -> dict[str, Any]:
    image_path = resolve_manifest_path(manifest_path, row.image_path)
    label_path = resolve_manifest_path(manifest_path, row.label_path)
    image = load_grayscale(image_path)
    gt_boxes = _load_gt_boxes(label_path)
    detections = detect_particles(image)
    segmentations = segment_detections(image, detections)
    matches = match_detections(detections, gt_boxes, iou_threshold=match_iou)
    tp = len(matches)
    fp = max(0, len(detections) - tp)
    fn = max(0, len(gt_boxes) - tp)
    detection_metrics = precision_recall_f1(tp=tp, fp=fp, fn=fn)

    particle_rows: list[dict[str, Any]] = []
    centers: list[tuple[float, float]] = []
    masks = [item.mask for item in segmentations]
    for index, item in enumerate(segmentations):
        stats = mask_stats(item.mask, nm_per_px=row.nm_per_px)
        centers.append(item.detection.center)
        particle_rows.append(
            {
                "particle_index": index,
                "box": [round(value, 3) for value in item.detection.box],
                "score": round(item.detection.score, 4),
                "center_px": [round(value, 3) for value in item.detection.center],
                "measurement": stats,
            }
        )

    overlay_path = output_dir / "overlays" / f"{row.image_id}_overlay.png"
    save_overlay(image=image, gt_boxes=gt_boxes, detections=detections, masks=masks, output_path=overlay_path)
    diameters = [
        float(item["measurement"]["equivalent_diameter_nm"])
        for item in particle_rows
        if item["measurement"]["equivalent_diameter_nm"] is not None
    ]
    nearest = nearest_neighbor_distances_nm(centers, nm_per_px=row.nm_per_px)
    return {
        "image_id": row.image_id,
        "split": row.split,
        "nm_per_px": row.nm_per_px,
        "gt_count": len(gt_boxes),
        "pred_count": len(detections),
        "matches": [{"prediction": p, "ground_truth": g, "box_iou": iou} for p, g, iou in matches],
        "detection": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            **detection_metrics,
        },
        "diameter_nm": summarize_values(diameters),
        "nearest_neighbor_nm": summarize_values(nearest),
        "particles": particle_rows,
        "overlay_path": str(overlay_path.relative_to(output_dir)).replace("\\", "/"),
    }


def _write_summary_markdown(report: dict[str, Any], output_path: Path) -> Path:
    lines = [
        "# Synthetic TEM Particle Analysis Demo Summary",
        "",
        "This report was generated from synthetic public-demo images only.",
        "",
        "## Aggregate Metrics",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    aggregate = report["aggregate"]
    for key in ("image_count", "gt_count", "pred_count", "precision", "recall", "f1"):
        value = aggregate[key]
        if isinstance(value, float):
            value = f"{value:.3f}"
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Per-Image Results", "", "| image | gt | pred | f1 | median diameter nm | overlay |", "|---|---:|---:|---:|---:|---|"])
    for row in report["images"]:
        median = row["diameter_nm"]["median"]
        median_text = "NA" if median is None else f"{median:.3f}"
        lines.append(
            f"| {row['image_id']} | {row['gt_count']} | {row['pred_count']} | {row['detection']['f1']:.3f} | {median_text} | `{row['overlay_path']}` |"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def run_pipeline(manifest_path: Path, output_dir: Path, match_iou: float = 0.3) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    validate_manifest(manifest_path)
    rows = read_manifest(manifest_path)
    image_reports = [_analyze_row(manifest_path, row, output_dir, match_iou=match_iou) for row in rows]
    gt_count = sum(row["gt_count"] for row in image_reports)
    pred_count = sum(row["pred_count"] for row in image_reports)
    tp = sum(row["detection"]["tp"] for row in image_reports)
    fp = sum(row["detection"]["fp"] for row in image_reports)
    fn = sum(row["detection"]["fn"] for row in image_reports)
    aggregate = {
        "image_count": len(image_reports),
        "gt_count": gt_count,
        "pred_count": pred_count,
        **precision_recall_f1(tp=tp, fp=fp, fn=fn),
    }
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "demo_policy": {
            "data": "synthetic_generated_only",
            "weights": "none",
            "raw_research_images": "not_included",
            "purpose": "public_job_search_demo",
        },
        "manifest": str(manifest_path),
        "match_iou": float(match_iou),
        "aggregate": aggregate,
        "images": image_reports,
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_summary_markdown(report, output_dir / "summary.md")
    return report
