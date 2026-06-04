from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .detector import Box, Detection


def _draw_box(draw: ImageDraw.ImageDraw, box: Box, color: tuple[int, int, int, int], width: int = 2) -> None:
    draw.rectangle([float(value) for value in box], outline=color, width=width)


def save_overlay(
    image: np.ndarray,
    gt_boxes: list[Box],
    detections: list[Detection],
    masks: list[np.ndarray],
    output_path: Path,
) -> Path:
    base = Image.fromarray(np.asarray(image, dtype=np.uint8), mode="L").convert("RGBA")
    mask_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for mask in masks:
        color = Image.new("RGBA", base.size, (64, 145, 210, 80))
        alpha = Image.fromarray(np.asarray(mask, dtype=np.uint8) * 255, mode="L")
        mask_layer = Image.composite(color, mask_layer, alpha)
    combined = Image.alpha_composite(base, mask_layer)
    draw = ImageDraw.Draw(combined, "RGBA")
    for box in gt_boxes:
        _draw_box(draw, box, (0, 210, 120, 230), width=2)
    for detection in detections:
        _draw_box(draw, detection.box, (45, 120, 255, 235), width=1)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.convert("RGB").save(output_path)
    return output_path
