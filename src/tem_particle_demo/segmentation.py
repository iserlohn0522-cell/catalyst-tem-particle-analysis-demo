from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detector import Box, Detection, connected_components, detection_threshold


@dataclass(frozen=True)
class SegmentationResult:
    detection: Detection
    mask: np.ndarray


def _clip_box(box: Box, width: int, height: int, pad: int) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return (
        max(0, int(np.floor(x1)) - pad),
        max(0, int(np.floor(y1)) - pad),
        min(width, int(np.ceil(x2)) + pad),
        min(height, int(np.ceil(y2)) + pad),
    )


def segment_from_box_prompt(image: np.ndarray, box: Box, threshold: int | None = None, pad: int = 3) -> np.ndarray:
    gray = np.asarray(image, dtype=np.uint8)
    height, width = gray.shape
    x1, y1, x2, y2 = _clip_box(box, width=width, height=height, pad=pad)
    if x2 <= x1 or y2 <= y1:
        return np.zeros_like(gray, dtype=bool)
    local = gray[y1:y2, x1:x2]
    cutoff = detection_threshold(gray) if threshold is None else int(threshold)
    local_mask = local < cutoff
    components = connected_components(local_mask)
    if not components:
        return np.zeros_like(gray, dtype=bool)
    cx = (box[0] + box[2]) * 0.5 - x1
    cy = (box[1] + box[3]) * 0.5 - y1

    def rank(component: np.ndarray) -> tuple[float, int]:
        ys, xs = np.where(component)
        if len(xs) == 0:
            return (-1e9, 0)
        distance = float(np.hypot(float(xs.mean()) - cx, float(ys.mean()) - cy))
        return (-distance, int(component.sum()))

    selected = max(components, key=rank)
    mask = np.zeros_like(gray, dtype=bool)
    mask[y1:y2, x1:x2] = selected
    return mask


def segment_detections(image: np.ndarray, detections: list[Detection]) -> list[SegmentationResult]:
    return [SegmentationResult(detection=detection, mask=segment_from_box_prompt(image, detection.box)) for detection in detections]
