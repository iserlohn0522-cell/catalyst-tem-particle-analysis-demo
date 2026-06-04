from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from .detector import Box, Detection


def box_area(box: Box) -> float:
    return max(0.0, float(box[2]) - float(box[0])) * max(0.0, float(box[3]) - float(box[1]))


def box_iou(a: Box, b: Box) -> float:
    ix1 = max(float(a[0]), float(b[0]))
    iy1 = max(float(a[1]), float(b[1]))
    ix2 = min(float(a[2]), float(b[2]))
    iy2 = min(float(a[3]), float(b[3]))
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = box_area(a) + box_area(b) - inter
    return float(inter / union) if union > 0 else 0.0


def mask_iou(a: np.ndarray, b: np.ndarray) -> float:
    a_bool = np.asarray(a, dtype=bool)
    b_bool = np.asarray(b, dtype=bool)
    if a_bool.shape != b_bool.shape:
        raise ValueError("Masks must have matching shapes")
    inter = np.logical_and(a_bool, b_bool).sum()
    union = np.logical_or(a_bool, b_bool).sum()
    return float(inter / union) if union else 0.0


def match_detections(
    detections: Sequence[Detection],
    gt_boxes: Sequence[Box],
    iou_threshold: float = 0.3,
) -> list[tuple[int, int, float]]:
    candidates: list[tuple[int, int, float, float]] = []
    for pred_index, detection in enumerate(detections):
        for gt_index, gt_box in enumerate(gt_boxes):
            iou = box_iou(detection.box, gt_box)
            if iou >= iou_threshold:
                candidates.append((pred_index, gt_index, iou, detection.score))
    candidates.sort(key=lambda item: (-item[3], -item[2]))
    matched_pred: set[int] = set()
    matched_gt: set[int] = set()
    matches: list[tuple[int, int, float]] = []
    for pred_index, gt_index, iou, _score in candidates:
        if pred_index in matched_pred or gt_index in matched_gt:
            continue
        matched_pred.add(pred_index)
        matched_gt.add(gt_index)
        matches.append((pred_index, gt_index, iou))
    return matches


def precision_recall_f1(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def mask_stats(mask: np.ndarray, nm_per_px: float) -> dict[str, float | int | None]:
    mask_bool = np.asarray(mask, dtype=bool)
    area_px = int(mask_bool.sum())
    if area_px == 0:
        return {
            "area_px": 0,
            "area_nm2": None,
            "equivalent_diameter_px": None,
            "equivalent_diameter_nm": None,
            "perimeter_px": None,
            "circularity": None,
        }
    padded = np.pad(mask_bool.astype(np.int16), 1, mode="constant", constant_values=0)
    perimeter = int(np.abs(np.diff(padded, axis=0)).sum() + np.abs(np.diff(padded, axis=1)).sum())
    eq_diameter_px = float(2.0 * math.sqrt(area_px / math.pi))
    area_nm2 = float(area_px * nm_per_px * nm_per_px)
    return {
        "area_px": area_px,
        "area_nm2": area_nm2,
        "equivalent_diameter_px": eq_diameter_px,
        "equivalent_diameter_nm": float(eq_diameter_px * nm_per_px),
        "perimeter_px": perimeter,
        "circularity": float((4.0 * math.pi * area_px) / (perimeter * perimeter)) if perimeter else None,
    }


def nearest_neighbor_distances_nm(centers: Sequence[tuple[float, float]], nm_per_px: float) -> list[float]:
    if len(centers) < 2:
        return []
    distances: list[float] = []
    for index, center in enumerate(centers):
        cx, cy = center
        nearest = min(
            math.hypot(cx - ox, cy - oy)
            for other_index, (ox, oy) in enumerate(centers)
            if other_index != index
        )
        distances.append(float(nearest * nm_per_px))
    return distances


def summarize_values(values: Sequence[float]) -> dict[str, float | int | None]:
    clean = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not clean:
        return {"n": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "n": len(clean),
        "mean": float(sum(clean) / len(clean)),
        "median": float(clean[len(clean) // 2] if len(clean) % 2 else (clean[len(clean) // 2 - 1] + clean[len(clean) // 2]) / 2.0),
        "min": float(clean[0]),
        "max": float(clean[-1]),
    }
