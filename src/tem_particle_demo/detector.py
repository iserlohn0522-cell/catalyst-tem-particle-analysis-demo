from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image


Box = tuple[float, float, float, float]


@dataclass(frozen=True)
class Detection:
    box: Box
    score: float
    area_px: int
    center: tuple[float, float]


def load_grayscale(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("L"), dtype=np.uint8)


def _neighbors(y: int, x: int, height: int, width: int) -> Iterable[tuple[int, int]]:
    for yy in (y - 1, y, y + 1):
        for xx in (x - 1, x, x + 1):
            if yy == y and xx == x:
                continue
            if 0 <= yy < height and 0 <= xx < width:
                yield yy, xx


def connected_components(mask: np.ndarray) -> list[np.ndarray]:
    mask_bool = np.asarray(mask, dtype=bool)
    height, width = mask_bool.shape
    visited = np.zeros_like(mask_bool, dtype=bool)
    components: list[np.ndarray] = []
    ys, xs = np.where(mask_bool)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if visited[y0, x0]:
            continue
        stack = [(y0, x0)]
        visited[y0, x0] = True
        points: list[tuple[int, int]] = []
        while stack:
            y, x = stack.pop()
            points.append((y, x))
            for yy, xx in _neighbors(y, x, height, width):
                if mask_bool[yy, xx] and not visited[yy, xx]:
                    visited[yy, xx] = True
                    stack.append((yy, xx))
        component = np.zeros_like(mask_bool, dtype=bool)
        yy = [point[0] for point in points]
        xx = [point[1] for point in points]
        component[yy, xx] = True
        components.append(component)
    return components


def detection_threshold(image: np.ndarray) -> int:
    gray = np.asarray(image, dtype=np.uint8)
    return int(min(135, max(75, np.percentile(gray, 18) + 22)))


def detect_particles(image: np.ndarray, threshold: int | None = None, min_area: int = 20) -> list[Detection]:
    gray = np.asarray(image, dtype=np.uint8)
    cutoff = detection_threshold(gray) if threshold is None else int(threshold)
    dark_mask = gray < cutoff
    detections: list[Detection] = []
    for component in connected_components(dark_mask):
        area = int(component.sum())
        if area < min_area:
            continue
        ys, xs = np.where(component)
        x1 = float(xs.min())
        y1 = float(ys.min())
        x2 = float(xs.max() + 1)
        y2 = float(ys.max() + 1)
        if x2 - x1 < 3 or y2 - y1 < 3:
            continue
        mean_inside = float(gray[component].mean())
        score = float(np.clip((cutoff - mean_inside) / max(1.0, cutoff), 0.05, 1.0))
        detections.append(
            Detection(
                box=(x1, y1, x2, y2),
                score=score,
                area_px=area,
                center=(float(xs.mean()), float(ys.mean())),
            )
        )
    return sorted(detections, key=lambda item: item.score, reverse=True)
