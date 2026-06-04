from __future__ import annotations

import numpy as np
import pytest

from tem_particle_demo.detector import Detection
from tem_particle_demo.metrics import box_iou, mask_iou, mask_stats, match_detections, nearest_neighbor_distances_nm


def test_box_and_mask_iou() -> None:
    assert box_iou((0, 0, 10, 10), (0, 0, 10, 10)) == pytest.approx(1.0)
    assert box_iou((0, 0, 10, 10), (20, 20, 30, 30)) == pytest.approx(0.0)

    a = np.zeros((8, 8), dtype=bool)
    b = np.zeros((8, 8), dtype=bool)
    a[1:5, 1:5] = True
    b[3:7, 3:7] = True
    assert mask_iou(a, b) == pytest.approx(4 / 28)


def test_matching_is_one_to_one() -> None:
    detections = [
        Detection(box=(0, 0, 10, 10), score=0.9, area_px=100, center=(5, 5)),
        Detection(box=(1, 1, 9, 9), score=0.8, area_px=64, center=(5, 5)),
    ]
    matches = match_detections(detections, [(0, 0, 10, 10)], iou_threshold=0.3)

    assert matches == [(0, 0, 1.0)]


def test_mask_stats_and_nearest_neighbor() -> None:
    mask = np.zeros((20, 20), dtype=bool)
    mask[5:15, 5:15] = True
    stats = mask_stats(mask, nm_per_px=0.2)

    assert stats["area_px"] == 100
    assert stats["area_nm2"] == pytest.approx(4.0)
    assert stats["equivalent_diameter_nm"] == pytest.approx(2.256758, rel=1e-5)
    assert stats["circularity"] is not None

    distances = nearest_neighbor_distances_nm([(0, 0), (3, 4), (10, 0)], nm_per_px=0.5)
    assert distances == pytest.approx([2.5, 2.5, pytest.approx(4.031128874)])
